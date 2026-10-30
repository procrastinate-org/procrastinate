CREATE FUNCTION procrastinate_finish_job_v2(
    job_id bigint,
    end_status procrastinate_job_status,
    delete_job boolean,
    expected_status procrastinate_job_status,
    expected_attempts integer
)
    RETURNS boolean
    LANGUAGE plpgsql
AS $$
BEGIN
    PERFORM 1 FROM procrastinate_jobs AS jobs
    WHERE jobs.id = job_id
        AND jobs.status = expected_status
        AND jobs.attempts = expected_attempts
    FOR UPDATE;
    IF NOT FOUND THEN
        RETURN false;
    END IF;
    PERFORM procrastinate_finish_job_v1(job_id, end_status, delete_job);
    RETURN true;
END;
$$;

CREATE FUNCTION procrastinate_retry_job_v3(
    job_id bigint,
    retry_at timestamp with time zone,
    new_priority integer,
    new_queue_name character varying,
    new_lock character varying,
    expected_status procrastinate_job_status,
    expected_attempts integer
)
    RETURNS boolean
    LANGUAGE plpgsql
AS $$
BEGIN
    PERFORM 1 FROM procrastinate_jobs AS jobs
    WHERE jobs.id = job_id
        AND jobs.status = expected_status
        AND jobs.attempts = expected_attempts
    FOR UPDATE;
    IF NOT FOUND THEN
        RETURN false;
    END IF;
    PERFORM procrastinate_retry_job_v2(job_id, retry_at, new_priority, new_queue_name, new_lock);
    RETURN true;
END;
$$;

CREATE OR REPLACE FUNCTION procrastinate_notify_queue_abort_job_v1()
RETURNS trigger
    LANGUAGE plpgsql
AS $$
DECLARE
    payload TEXT;
BEGIN
    SELECT json_build_object(
        'type', 'abort_job_requested',
        'job_id', NEW.id,
        'attempts', NEW.attempts
    )::text INTO payload;
    PERFORM pg_notify('procrastinate_queue_v1#' || NEW.queue_name, payload);
    PERFORM pg_notify('procrastinate_any_queue_v1', payload);
    RETURN NEW;
END;
$$;
