CREATE OR REPLACE FUNCTION procrastinate_notify_queue_job_inserted()
RETURNS trigger
    LANGUAGE plpgsql
AS $$
DECLARE
    payload TEXT;
BEGIN
    SELECT json_object('type': 'job_inserted', 'job_id': NEW.id)::text INTO payload;
	PERFORM pg_notify('procrastinate_queue#' || NEW.queue_name, payload);
	PERFORM pg_notify('procrastinate_any_queue', payload);
	RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS procrastinate_jobs_notify_queue ON procrastinate_jobs;

CREATE TRIGGER procrastinate_jobs_notify_queue_job_inserted
    AFTER INSERT ON procrastinate_jobs
    FOR EACH ROW WHEN ((new.status = 'todo'::procrastinate_job_status))
    EXECUTE PROCEDURE procrastinate_notify_queue_job_inserted();

DROP FUNCTION IF EXISTS procrastinate_notify_queue;

CREATE OR REPLACE FUNCTION procrastinate_notify_queue_abort_job()
RETURNS trigger
    LANGUAGE plpgsql
AS $$
DECLARE
    payload TEXT;
BEGIN
    SELECT json_object('type': 'abort_job_requested', 'job_id': NEW.id)::text INTO payload;
	PERFORM pg_notify('procrastinate_queue#' || NEW.queue_name, payload);
	PERFORM pg_notify('procrastinate_any_queue', payload);
	RETURN NEW;
END;
$$;

CREATE TRIGGER procrastinate_jobs_notify_queue_abort_job
    AFTER UPDATE OF abort_requested ON procrastinate_jobs
    FOR EACH ROW WHEN ((old.abort_requested = false AND new.abort_requested = true AND new.status = 'doing'::procrastinate_job_status))
    EXECUTE PROCEDURE procrastinate_notify_queue_abort_job();

CREATE OR REPLACE FUNCTION procrastinate_retry_job(
    job_id bigint,
    retry_at timestamp with time zone,
    new_priority integer,
    new_queue_name character varying,
    new_lock character varying
)
    RETURNS void
    LANGUAGE plpgsql
AS $$
DECLARE
    _job_id bigint;
BEGIN
    UPDATE procrastinate_jobs
    SET status = CASE
            WHEN NOT abort_requested THEN 'todo'::procrastinate_job_status
            ELSE 'failed'::procrastinate_job_status
        END,
        attempts = CASE
            WHEN NOT abort_requested THEN attempts + 1
            ELSE attempts
        END,
        scheduled_at = CASE
            WHEN NOT abort_requested THEN retry_at
            ELSE scheduled_at
        END,
        priority = CASE
            WHEN NOT abort_requested THEN COALESCE(new_priority, priority)
            ELSE priority
        END,
        queue_name = CASE
            WHEN NOT abort_requested THEN COALESCE(new_queue_name, queue_name)
            ELSE queue_name
        END,
        lock = CASE
            WHEN NOT abort_requested THEN COALESCE(new_lock, lock)
            ELSE lock
        END
    WHERE id = job_id AND status = 'doing'
    RETURNING id INTO _job_id;
    IF _job_id IS NULL THEN
        RAISE 'Job was not found or not in "doing" status (job id: %)', job_id;
    END IF;
END;
$$;
