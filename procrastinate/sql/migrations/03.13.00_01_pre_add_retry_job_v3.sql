-- Migration: Add procrastinate_retry_job_v3, which returns the job's new status
CREATE FUNCTION procrastinate_retry_job_v3(
    job_id bigint,
    retry_at timestamp with time zone,
    new_priority integer,
    new_queue_name character varying,
    new_lock character varying
) RETURNS procrastinate_job_status LANGUAGE plpgsql AS $$
DECLARE
    _new_status procrastinate_job_status;
    _abort_requested boolean;
    _current_status procrastinate_job_status;
BEGIN
    SELECT status, abort_requested FROM procrastinate_jobs
    WHERE id = job_id AND status IN ('doing', 'failed')
    FOR UPDATE
    INTO _current_status, _abort_requested;
    IF _current_status = 'doing' AND _abort_requested THEN
        UPDATE procrastinate_jobs
        SET status = 'failed'::procrastinate_job_status
        WHERE id = job_id AND status = 'doing'
        RETURNING status INTO _new_status;
    ELSE
        BEGIN
            UPDATE procrastinate_jobs
            SET status = 'todo'::procrastinate_job_status,
                attempts = attempts + 1,
                scheduled_at = retry_at,
                priority = COALESCE(new_priority, priority),
                queue_name = COALESCE(new_queue_name, queue_name),
                lock = COALESCE(new_lock, lock)
            WHERE id = job_id AND status IN ('doing', 'failed')
            RETURNING status INTO _new_status;
        EXCEPTION WHEN unique_violation THEN
            -- Another job with the same queueing lock is already waiting in "todo",
            -- and it will do the same work. A "doing" job that cannot be retried
            -- is closed as failed, otherwise it would keep its lock forever.
            -- A "failed" job holds no lock, so the error is raised as before.
            IF _current_status IS DISTINCT FROM 'doing' THEN
                RAISE;
            END IF;
            UPDATE procrastinate_jobs
            SET status = 'failed'::procrastinate_job_status,
                attempts = attempts + 1
            WHERE id = job_id AND status = 'doing'
            RETURNING status INTO _new_status;
        END;
    END IF;

    IF _new_status IS NULL THEN
        RAISE 'Job was not found or has an invalid status to retry (job id: %)', job_id;
    END IF;

    RETURN _new_status;
END;
$$;
