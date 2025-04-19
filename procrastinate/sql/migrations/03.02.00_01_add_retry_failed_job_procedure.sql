-- Append new event type to reflect transition from failed -> todo
ALTER TYPE procrastinate_job_event_type ADD VALUE 'retried' AFTER 'scheduled';

-- Procedure to retry failed jobs
CREATE FUNCTION procrastinate_retry_failed_job_v1(
    job_id bigint,
    new_priority integer,
    new_queue_name character varying,
    new_lock character varying
) RETURNS void LANGUAGE plpgsql AS $$
DECLARE
    _job_id bigint;
BEGIN
    UPDATE procrastinate_jobs
    SET status = 'todo'::procrastinate_job_status,
        attempts = attempts + 1,
        priority = COALESCE(new_priority, priority),
        queue_name = COALESCE(new_queue_name, queue_name),
        lock = COALESCE(new_lock, lock)
    WHERE id = job_id AND status = 'failed'
    RETURNING id INTO _job_id;

    IF _job_id IS NULL THEN
        RAISE 'Job was not found or not in "failed" status (job id: %)', job_id;
    END IF;
END;
$$;

DROP TRIGGER IF EXISTS procrastinate_trigger_status_events_update_v1 ON procrastinate_jobs;
DROP FUNCTION IF EXISTS public.procrastinate_trigger_function_status_events_update_v1;

CREATE FUNCTION public.procrastinate_trigger_function_status_events_update_v1()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    WITH t AS (
        SELECT CASE
            WHEN OLD.status = 'todo'::procrastinate_job_status
                AND NEW.status = 'doing'::procrastinate_job_status
                THEN 'started'::procrastinate_job_event_type
            WHEN OLD.status = 'doing'::procrastinate_job_status
                AND NEW.status = 'todo'::procrastinate_job_status
                THEN 'deferred_for_retry'::procrastinate_job_event_type
            WHEN OLD.status = 'doing'::procrastinate_job_status
                AND NEW.status = 'failed'::procrastinate_job_status
                THEN 'failed'::procrastinate_job_event_type
            WHEN OLD.status = 'doing'::procrastinate_job_status
                AND NEW.status = 'succeeded'::procrastinate_job_status
                THEN 'succeeded'::procrastinate_job_event_type
            WHEN OLD.status = 'todo'::procrastinate_job_status
                AND (
                    NEW.status = 'cancelled'::procrastinate_job_status
                    OR NEW.status = 'failed'::procrastinate_job_status
                    OR NEW.status = 'succeeded'::procrastinate_job_status
                )
                THEN 'cancelled'::procrastinate_job_event_type
            WHEN OLD.status = 'doing'::procrastinate_job_status
                AND NEW.status = 'aborted'::procrastinate_job_status
                THEN 'aborted'::procrastinate_job_event_type
            WHEN OLD.status = 'failed'::procrastinate_job_status
                AND NEW.status = 'todo'::procrastinate_job_status
                THEN 'retried'::procrastinate_job_event_type
            ELSE NULL
        END as event_type
    )
    INSERT INTO procrastinate_events(job_id, type)
        SELECT NEW.id, t.event_type
        FROM t
        WHERE t.event_type IS NOT NULL;
	RETURN NEW;
END;
$function$;

CREATE TRIGGER procrastinate_trigger_status_events_update_v1
    AFTER UPDATE OF status ON procrastinate_jobs
    FOR EACH ROW
    EXECUTE PROCEDURE procrastinate_trigger_function_status_events_update_v1();
