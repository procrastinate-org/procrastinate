-- Add an 'abort_requested' column to the procrastinate_jobs table
ALTER TABLE procrastinate_jobs ADD COLUMN abort_requested boolean DEFAULT false NOT NULL;

-- Set abort requested flag on all jobs with 'aborting' status
UPDATE procrastinate_jobs SET abort_requested = true WHERE status = 'aborting';

-- Delete the indexes that depends on the old status and enum type
DROP INDEX IF EXISTS procrastinate_jobs_queueing_lock_idx;
DROP INDEX IF EXISTS procrastinate_jobs_lock_idx;
DROP INDEX IF EXISTS procrastinate_jobs_id_lock_idx;

-- Delete the triggers that depends on the old status type (to recreate them later)
DROP TRIGGER IF EXISTS procrastinate_jobs_notify_queue ON procrastinate_jobs;
DROP TRIGGER IF EXISTS procrastinate_trigger_status_events_update ON procrastinate_jobs;
DROP TRIGGER IF EXISTS procrastinate_trigger_status_events_insert ON procrastinate_jobs;
DROP TRIGGER IF EXISTS procrastinate_trigger_scheduled_events ON procrastinate_jobs;

-- Delete the functions that depends on the old status type
DROP FUNCTION IF EXISTS procrastinate_fetch_job;
DROP FUNCTION IF EXISTS procrastinate_finish_job(bigint, procrastinate_job_status, boolean);
DROP FUNCTION IF EXISTS procrastinate_cancel_job;
DROP FUNCTION IF EXISTS procrastinate_trigger_status_events_procedure_update;
DROP FUNCTION IF EXISTS procrastinate_finish_job(integer, procrastinate_job_status, timestamp with time zone, boolean);

-- Create a new enum type without 'aborting'
CREATE TYPE procrastinate_job_status_new AS ENUM (
    'todo',
    'doing',
    'succeeded',
    'failed',
    'cancelled',
    'aborted'
);

-- We need to drop the default temporarily as otherwise DatatypeMismatch would occur
ALTER TABLE procrastinate_jobs ALTER COLUMN status DROP DEFAULT;

-- Alter the table to use the new type
ALTER TABLE procrastinate_jobs
ALTER COLUMN status TYPE procrastinate_job_status_new
USING (
    CASE status::text
        WHEN 'aborting' THEN 'doing'::procrastinate_job_status_new
        ELSE status::text::procrastinate_job_status_new
    END
);

-- Recreate the default
ALTER TABLE procrastinate_jobs ALTER COLUMN status SET DEFAULT 'todo'::procrastinate_job_status_new;

-- Drop the old type
DROP TYPE procrastinate_job_status;

-- Rename the new type to the original name
ALTER TYPE procrastinate_job_status_new RENAME TO procrastinate_job_status;

-- Recreate the indexes
CREATE UNIQUE INDEX procrastinate_jobs_queueing_lock_idx ON procrastinate_jobs (queueing_lock) WHERE status = 'todo';
CREATE UNIQUE INDEX procrastinate_jobs_lock_idx ON procrastinate_jobs (lock) WHERE status = 'doing';
CREATE INDEX procrastinate_jobs_id_lock_idx ON procrastinate_jobs (id, lock) WHERE status = ANY (ARRAY['todo'::procrastinate_job_status, 'doing'::procrastinate_job_status]);

-- Create a new constraint
ALTER TABLE procrastinate_jobs
    ADD CONSTRAINT procrastinate_jobs_no_aborting_todo CHECK (NOT (status = 'todo' AND abort_requested));

-- Recreate and update the functions
CREATE OR REPLACE FUNCTION procrastinate_fetch_job(
    target_queue_names character varying[]
)
    RETURNS procrastinate_jobs
    LANGUAGE plpgsql
AS $$
DECLARE
	found_jobs procrastinate_jobs;
BEGIN
    WITH candidate AS (
        SELECT jobs.*
            FROM procrastinate_jobs AS jobs
            WHERE
                -- reject the job if its lock has earlier jobs
                NOT EXISTS (
                    SELECT 1
                        FROM procrastinate_jobs AS earlier_jobs
                        WHERE
                            jobs.lock IS NOT NULL
                            AND earlier_jobs.lock = jobs.lock
                            AND earlier_jobs.status IN ('todo', 'doing')
                            AND earlier_jobs.id < jobs.id)
                AND jobs.status = 'todo'
                AND (target_queue_names IS NULL OR jobs.queue_name = ANY( target_queue_names ))
                AND (jobs.scheduled_at IS NULL OR jobs.scheduled_at <= now())
            ORDER BY jobs.priority DESC, jobs.id ASC LIMIT 1
            FOR UPDATE OF jobs SKIP LOCKED
    )
    UPDATE procrastinate_jobs
        SET status = 'doing'
        FROM candidate
        WHERE procrastinate_jobs.id = candidate.id
        RETURNING procrastinate_jobs.* INTO found_jobs;

	RETURN found_jobs;
END;
$$;

CREATE FUNCTION procrastinate_finish_job(job_id bigint, end_status procrastinate_job_status, delete_job boolean)
    RETURNS void
    LANGUAGE plpgsql
AS $$
DECLARE
    _job_id bigint;
BEGIN
    IF end_status NOT IN ('succeeded', 'failed', 'aborted') THEN
        RAISE 'End status should be either "succeeded", "failed" or "aborted" (job id: %)', job_id;
    END IF;
    IF delete_job THEN
        DELETE FROM procrastinate_jobs
        WHERE id = job_id AND status IN ('todo', 'doing')
        RETURNING id INTO _job_id;
    ELSE
        UPDATE procrastinate_jobs
        SET status = end_status,
            abort_requested = false,
            attempts = CASE status
                WHEN 'doing' THEN attempts + 1 ELSE attempts
            END
        WHERE id = job_id AND status IN ('todo', 'doing')
        RETURNING id INTO _job_id;
    END IF;
    IF _job_id IS NULL THEN
        RAISE 'Job was not found or not in "doing" or "todo" status (job id: %)', job_id;
    END IF;
END;
$$;

CREATE FUNCTION procrastinate_cancel_job(job_id bigint, abort boolean, delete_job boolean)
    RETURNS bigint
    LANGUAGE plpgsql
AS $$
DECLARE
    _job_id bigint;
BEGIN
    IF delete_job THEN
        DELETE FROM procrastinate_jobs
        WHERE id = job_id AND status = 'todo'
        RETURNING id INTO _job_id;
    END IF;
    IF _job_id IS NULL THEN
        IF abort THEN
            UPDATE procrastinate_jobs
            SET abort_requested = true,
                status = CASE status
                    WHEN 'todo' THEN 'cancelled'::procrastinate_job_status ELSE status
                END
            WHERE id = job_id AND status IN ('todo', 'doing')
            RETURNING id INTO _job_id;
        ELSE
            UPDATE procrastinate_jobs
            SET status = 'cancelled'::procrastinate_job_status
            WHERE id = job_id AND status = 'todo'
            RETURNING id INTO _job_id;
        END IF;
    END IF;
    RETURN _job_id;
END;
$$;

CREATE FUNCTION procrastinate_trigger_status_events_procedure_update()
    RETURNS trigger
    LANGUAGE plpgsql
AS $$
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

CREATE FUNCTION procrastinate_finish_job(job_id integer, end_status procrastinate_job_status, next_scheduled_at timestamp with time zone, delete_job boolean)
    RETURNS void
    LANGUAGE plpgsql
AS $$
DECLARE
    _job_id bigint;
BEGIN
    IF end_status NOT IN ('succeeded', 'failed') THEN
        RAISE 'End status should be either "succeeded" or "failed" (job id: %)', job_id;
    END IF;
    IF delete_job THEN
        DELETE FROM procrastinate_jobs
        WHERE id = job_id AND status IN ('todo', 'doing')
        RETURNING id INTO _job_id;
    ELSE
        UPDATE procrastinate_jobs
        SET status = end_status,
            abort_requested = false,
            attempts =
                CASE
                    WHEN status = 'doing' THEN attempts + 1
                    ELSE attempts
                END
        WHERE id = job_id AND status IN ('todo', 'doing')
        RETURNING id INTO _job_id;
    END IF;
    IF _job_id IS NULL THEN
        RAISE 'Job was not found or not in "doing" or "todo" status (job id: %)', job_id;
    END IF;
END;
$$;

-- Recreate the deleted triggers
CREATE TRIGGER procrastinate_jobs_notify_queue
    AFTER INSERT ON procrastinate_jobs
    FOR EACH ROW WHEN ((new.status = 'todo'::procrastinate_job_status))
    EXECUTE PROCEDURE procrastinate_notify_queue();

CREATE TRIGGER procrastinate_trigger_status_events_update
    AFTER UPDATE OF status ON procrastinate_jobs
    FOR EACH ROW
    EXECUTE PROCEDURE procrastinate_trigger_status_events_procedure_update();

CREATE TRIGGER procrastinate_trigger_status_events_insert
    AFTER INSERT ON procrastinate_jobs
    FOR EACH ROW WHEN ((new.status = 'todo'::procrastinate_job_status))
    EXECUTE PROCEDURE procrastinate_trigger_status_events_procedure_insert();

CREATE TRIGGER procrastinate_trigger_scheduled_events
    AFTER UPDATE OR INSERT ON procrastinate_jobs
    FOR EACH ROW WHEN ((new.scheduled_at IS NOT NULL AND new.status = 'todo'::procrastinate_job_status))
    EXECUTE PROCEDURE procrastinate_trigger_scheduled_events_procedure();

-- Create additional function and trigger for abortion requests
CREATE FUNCTION procrastinate_trigger_abort_requested_events_procedure()
    RETURNS trigger
    LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO procrastinate_events(job_id, type)
        VALUES (NEW.id, 'abort_requested'::procrastinate_job_event_type);
    RETURN NEW;
END;
$$;

CREATE TRIGGER procrastinate_trigger_abort_requested_events
    AFTER UPDATE OF abort_requested ON procrastinate_jobs
    FOR EACH ROW WHEN ((new.abort_requested = true))
    EXECUTE PROCEDURE procrastinate_trigger_abort_requested_events_procedure();

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
