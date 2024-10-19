-- These are old versions of functions, that we needed to keep around for
-- backwards compatibility. We can now safely drop them.
DROP FUNCTION IF EXISTS procrastinate_finish_job(
    integer,
    procrastinate_job_status,
    timestamp with time zone,
    boolean
);
DROP FUNCTION IF EXISTS procrastinate_defer_job(
    character varying,
    character varying,
    text,
    text,
    jsonb,
    timestamp with time zone
);
DROP FUNCTION IF EXISTS procrastinate_defer_periodic_job(
    character varying,
    character varying,
    character varying,
    character varying,
    character varying,
    bigint,
    jsonb
);
DROP FUNCTION IF EXISTS procrastinate_retry_job(
    bigint,
    timestamp with time zone
);
DROP FUNCTION IF EXISTS procrastinate_retry_job(
    bigint,
    timestamp with time zone,
    integer,
    character varying,
    character varying
);

-- Remove all traces of the "aborting" status
-- Last sanity update in case the trigger didn't work 100% of the time
UPDATE procrastinate_jobs SET abort_requested = true WHERE status = 'aborting';

DROP TRIGGER IF EXISTS procrastinate_trigger_sync_abort_requested_with_status_v1 ON procrastinate_jobs;
DROP FUNCTION IF EXISTS procrastinate_sync_abort_requested_with_status_v1;

-- We need to drop the default temporarily as otherwise DatatypeMismatch would occur
ALTER TABLE procrastinate_jobs ALTER COLUMN status DROP DEFAULT;

-- Delete the indexes that depends on the old status and enum type
DROP INDEX IF EXISTS procrastinate_jobs_queueing_lock_idx;
DROP INDEX IF EXISTS procrastinate_jobs_lock_idx;
DROP INDEX IF EXISTS procrastinate_jobs_id_lock_idx;

-- Delete the triggers that depends on the old status type (to recreate them later)
DROP TRIGGER IF EXISTS procrastinate_trigger_status_events_update ON procrastinate_jobs;
DROP TRIGGER IF EXISTS procrastinate_trigger_status_events_insert ON procrastinate_jobs;
DROP TRIGGER IF EXISTS procrastinate_trigger_scheduled_events ON procrastinate_jobs;
DROP TRIGGER IF EXISTS procrastinate_trigger_status_events_update_v1 ON procrastinate_jobs;
DROP TRIGGER IF EXISTS procrastinate_jobs_notify_queue_job_inserted_v1 ON procrastinate_jobs;

-- Delete the functions that depends on the old status type
DROP FUNCTION IF EXISTS procrastinate_fetch_job;
DROP FUNCTION IF EXISTS procrastinate_finish_job(bigint, procrastinate_job_status, boolean);
DROP FUNCTION IF EXISTS procrastinate_cancel_job;
DROP FUNCTION IF EXISTS procrastinate_trigger_status_events_procedure_update_v1;
DROP FUNCTION IF EXISTS procrastinate_finish_job(integer, procrastinate_job_status, timestamp with time zone, boolean);
DROP FUNCTION IF EXISTS procrastinate_notify_queue_job_inserted_v1;

-- Alter the table to use the new type
ALTER TABLE procrastinate_jobs
ALTER COLUMN status TYPE procrastinate_job_status_v1
USING (
    CASE status::text
        WHEN 'aborting' THEN 'doing'::procrastinate_job_status_v1
        ELSE status::text::procrastinate_job_status_v1
    END
);

-- Recreate the default
ALTER TABLE procrastinate_jobs ALTER COLUMN status SET DEFAULT 'todo'::procrastinate_job_status_v1;

-- Recreate the indexes
CREATE UNIQUE INDEX procrastinate_jobs_queueing_lock_idx ON procrastinate_jobs (queueing_lock) WHERE status = 'todo';
CREATE UNIQUE INDEX procrastinate_jobs_lock_idx ON procrastinate_jobs (lock) WHERE status = 'doing';
CREATE INDEX procrastinate_jobs_id_lock_idx ON procrastinate_jobs (id, lock) WHERE status = ANY (ARRAY['todo'::procrastinate_job_status_v1, 'doing'::procrastinate_job_status_v1]);

-- Drop the old type
DROP TYPE procrastinate_job_status;

-- Recreate or rename the triggers & their associated functions

ALTER FUNCTION procrastinate_trigger_status_events_procedure_insert
    RENAME TO procrastinate_trigger_function_status_events_insert_v1;

CREATE TRIGGER procrastinate_trigger_status_events_insert_v1
    AFTER INSERT ON procrastinate_jobs
    FOR EACH ROW WHEN ((new.status = 'todo'::procrastinate_job_status_v1))
    EXECUTE PROCEDURE procrastinate_trigger_function_status_events_insert_v1();

CREATE FUNCTION procrastinate_trigger_function_status_events_update_v2()
    RETURNS trigger
    LANGUAGE plpgsql
AS $$
BEGIN
    WITH t AS (
        SELECT CASE
            WHEN OLD.status = 'todo'::procrastinate_job_status_v1
                AND NEW.status = 'doing'::procrastinate_job_status_v1
                THEN 'started'::procrastinate_job_event_type
            WHEN OLD.status = 'doing'::procrastinate_job_status_v1
                AND NEW.status = 'todo'::procrastinate_job_status_v1
                THEN 'deferred_for_retry'::procrastinate_job_event_type
            WHEN OLD.status = 'doing'::procrastinate_job_status_v1
                AND NEW.status = 'failed'::procrastinate_job_status_v1
                THEN 'failed'::procrastinate_job_event_type
            WHEN OLD.status = 'doing'::procrastinate_job_status_v1
                AND NEW.status = 'succeeded'::procrastinate_job_status_v1
                THEN 'succeeded'::procrastinate_job_event_type
            WHEN OLD.status = 'todo'::procrastinate_job_status_v1
                AND (
                    NEW.status = 'cancelled'::procrastinate_job_status_v1
                    OR NEW.status = 'failed'::procrastinate_job_status_v1
                    OR NEW.status = 'succeeded'::procrastinate_job_status_v1
                )
                THEN 'cancelled'::procrastinate_job_event_type
            WHEN OLD.status = 'doing'::procrastinate_job_status_v1
                AND NEW.status = 'aborted'::procrastinate_job_status_v1
                THEN 'aborted'::procrastinate_job_event_type
            ELSE NULL
        END as event_type
    )
    INSERT INTO procrastinate_events(job_id, type)
        SELECT NEW.id, t.event_type
        FROM t
        WHERE t.event_type IS NOT NULL;
	RETURN NEW;
END;
$$;

CREATE TRIGGER procrastinate_trigger_status_events_update_v2
    AFTER UPDATE OF status ON procrastinate_jobs
    FOR EACH ROW
    EXECUTE PROCEDURE procrastinate_trigger_function_status_events_update_v2();

ALTER FUNCTION procrastinate_trigger_scheduled_events_procedure
    RENAME TO procrastinate_trigger_function_scheduled_events_v1;

CREATE TRIGGER procrastinate_trigger_scheduled_events_v1
    AFTER UPDATE OR INSERT ON procrastinate_jobs
    FOR EACH ROW WHEN ((new.scheduled_at IS NOT NULL AND new.status = 'todo'::procrastinate_job_status_v1))
    EXECUTE PROCEDURE procrastinate_trigger_function_scheduled_events_v1();

CREATE FUNCTION procrastinate_notify_queue_job_inserted_v2()
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

CREATE TRIGGER procrastinate_jobs_notify_queue_job_inserted_v2
    AFTER INSERT ON procrastinate_jobs
    FOR EACH ROW WHEN ((new.status = 'todo'::procrastinate_job_status_v1))
    EXECUTE PROCEDURE procrastinate_notify_queue_job_inserted_v2();


-- Create additional function and trigger for abortion requests
CREATE FUNCTION procrastinate_trigger_abort_requested_events_procedure_v1()
    RETURNS trigger
    LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO procrastinate_events(job_id, type)
        VALUES (NEW.id, 'abort_requested'::procrastinate_job_event_type);
    RETURN NEW;
END;
$$;

CREATE TRIGGER procrastinate_trigger_abort_requested_events_v1
    AFTER UPDATE OF abort_requested ON procrastinate_jobs
    FOR EACH ROW WHEN ((new.abort_requested = true))
    EXECUTE PROCEDURE procrastinate_trigger_abort_requested_events_procedure_v1();


CREATE FUNCTION procrastinate_notify_queue_abort_job_v1()
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

-- Create a new trigger that pushes a notification when a job is aborted
CREATE TRIGGER procrastinate_jobs_notify_queue_job_aborted_v1
    AFTER UPDATE OF abort_requested ON procrastinate_jobs
    FOR EACH ROW WHEN ((old.abort_requested = false AND new.abort_requested = true AND new.status = 'doing'::procrastinate_job_status_v1))
    EXECUTE PROCEDURE procrastinate_notify_queue_abort_job_v1();
