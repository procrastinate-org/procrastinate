-- Procrastinate Schema

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

-- Enums

CREATE TYPE procrastinate_job_status AS ENUM (
    'todo',  -- The job is queued
    'doing',  -- The job has been fetched by a worker
    'succeeded',  -- The job ended successfully
    'failed'  -- The job ended with an error
);

CREATE TYPE procrastinate_job_event_type AS ENUM (
    'deferred',  -- Job created, in todo
    'started',  -- todo -> doing
    'deferred_for_retry',  -- doing -> todo
    'failed',  -- doing -> failed
    'succeeded',  -- doing -> succeeded
    'cancelled', -- todo -> failed or succeeded
    'scheduled' -- not an event transition, but recording when a task is scheduled for
);

-- Tables

CREATE TABLE procrastinate_jobs (
    id bigserial PRIMARY KEY,
    queue_name character varying(128) NOT NULL,
    task_name character varying(128) NOT NULL,
    lock text,
    queueing_lock text,
    args jsonb DEFAULT '{}' NOT NULL,
    status procrastinate_job_status DEFAULT 'todo'::procrastinate_job_status NOT NULL,
    scheduled_at timestamp with time zone NULL,
    attempts integer DEFAULT 0 NOT NULL
);

CREATE TABLE procrastinate_periodic_defers (
    id bigserial PRIMARY KEY,
    task_name character varying(128) NOT NULL,
    defer_timestamp bigint,
    job_id bigint REFERENCES procrastinate_jobs(id) NULL,
    queue_name character varying(128) NULL,
    periodic_id character varying(128) NOT NULL DEFAULT '',
    CONSTRAINT procrastinate_periodic_defers_unique UNIQUE (task_name, periodic_id, defer_timestamp)
);

CREATE TABLE procrastinate_events (
    id BIGSERIAL PRIMARY KEY,
    job_id integer NOT NULL REFERENCES procrastinate_jobs ON DELETE CASCADE,
    type procrastinate_job_event_type,
    at timestamp with time zone DEFAULT NOW() NULL
);

-- Contraints & Indices

-- this prevents from having several jobs with the same queueing lock in the "todo" state
CREATE UNIQUE INDEX procrastinate_jobs_queueing_lock_idx ON procrastinate_jobs (queueing_lock) WHERE status = 'todo';
-- this prevents from having several jobs with the same lock in the "doing" state
CREATE UNIQUE INDEX procrastinate_jobs_lock_idx ON procrastinate_jobs (lock) WHERE status = 'doing';

CREATE INDEX procrastinate_jobs_queue_name_idx ON procrastinate_jobs(queue_name);
CREATE INDEX procrastinate_jobs_id_lock_idx ON procrastinate_jobs (id, lock) WHERE status = ANY (ARRAY['todo'::procrastinate_job_status, 'doing'::procrastinate_job_status]);

CREATE INDEX procrastinate_events_job_id_fkey ON procrastinate_events(job_id);

CREATE INDEX procrastinate_periodic_defers_job_id_fkey ON procrastinate_periodic_defers(job_id);


-- Functions

CREATE FUNCTION procrastinate_defer_job(
    queue_name character varying,
    task_name character varying,
    lock text,
    queueing_lock text,
    args jsonb,
    scheduled_at timestamp with time zone
) RETURNS bigint
    LANGUAGE plpgsql
AS $$
DECLARE
	job_id bigint;
BEGIN
    INSERT INTO procrastinate_jobs (queue_name, task_name, lock, queueing_lock, args, scheduled_at)
    VALUES (queue_name, task_name, lock, queueing_lock, args, scheduled_at)
    RETURNING id INTO job_id;

    RETURN job_id;
END;
$$;

CREATE FUNCTION procrastinate_defer_periodic_job(
    _queue_name character varying,
    _lock character varying,
    _queueing_lock character varying,
    _task_name character varying,
    _periodic_id character varying,
    _defer_timestamp bigint,
    _args jsonb
) RETURNS bigint
    LANGUAGE plpgsql
AS $$
DECLARE
	_job_id bigint;
	_defer_id bigint;
BEGIN

    INSERT
        INTO procrastinate_periodic_defers (task_name, periodic_id, defer_timestamp)
        VALUES (_task_name, _periodic_id, _defer_timestamp)
        ON CONFLICT DO NOTHING
        RETURNING id into _defer_id;

    IF _defer_id IS NULL THEN
        RETURN NULL;
    END IF;

    UPDATE procrastinate_periodic_defers
        SET job_id = procrastinate_defer_job(
                _queue_name,
                _task_name,
                _lock,
                _queueing_lock,
                _args,
                NULL
            )
        WHERE id = _defer_id
        RETURNING job_id INTO _job_id;

    DELETE
        FROM procrastinate_periodic_defers
        USING (
            SELECT id
            FROM procrastinate_periodic_defers
            WHERE procrastinate_periodic_defers.task_name = _task_name
            AND procrastinate_periodic_defers.periodic_id = _periodic_id
            AND procrastinate_periodic_defers.defer_timestamp < _defer_timestamp
            ORDER BY id
            FOR UPDATE
        ) to_delete
        WHERE procrastinate_periodic_defers.id = to_delete.id;

    RETURN _job_id;
END;
$$;

CREATE FUNCTION procrastinate_fetch_job(target_queue_names character varying[]) RETURNS procrastinate_jobs
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
            ORDER BY jobs.id ASC LIMIT 1
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

-- procrastinate_finish_job
-- the next_scheduled_at argument is kept for compatibility reasons, it is to be
-- removed after 1.0.0 is released
CREATE FUNCTION procrastinate_finish_job(job_id integer, end_status procrastinate_job_status, next_scheduled_at timestamp with time zone, delete_job boolean) RETURNS void
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

CREATE FUNCTION procrastinate_retry_job(job_id integer, retry_at timestamp with time zone) RETURNS void
    LANGUAGE plpgsql
AS $$
DECLARE
    _job_id bigint;
BEGIN
    UPDATE procrastinate_jobs
    SET status = 'todo',
        attempts = attempts + 1,
        scheduled_at = retry_at
    WHERE id = job_id AND status = 'doing'
    RETURNING id INTO _job_id;
    IF _job_id IS NULL THEN
        RAISE 'Job was not found or not in "doing" status (job id: %)', job_id;
    END IF;
END;
$$;

CREATE FUNCTION procrastinate_notify_queue() RETURNS trigger
    LANGUAGE plpgsql
AS $$
BEGIN
	PERFORM pg_notify('procrastinate_queue#' || NEW.queue_name, NEW.task_name);
	PERFORM pg_notify('procrastinate_any_queue', NEW.task_name);
	RETURN NEW;
END;
$$;

CREATE FUNCTION procrastinate_trigger_status_events_procedure_insert() RETURNS trigger
    LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO procrastinate_events(job_id, type)
        VALUES (NEW.id, 'deferred'::procrastinate_job_event_type);
	RETURN NEW;
END;
$$;

CREATE FUNCTION procrastinate_trigger_status_events_procedure_update() RETURNS trigger
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
                    NEW.status = 'failed'::procrastinate_job_status
                    OR NEW.status = 'succeeded'::procrastinate_job_status
                )
                THEN 'cancelled'::procrastinate_job_event_type
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

CREATE FUNCTION procrastinate_trigger_scheduled_events_procedure() RETURNS trigger
    LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO procrastinate_events(job_id, type, at)
        VALUES (NEW.id, 'scheduled'::procrastinate_job_event_type, NEW.scheduled_at);

	RETURN NEW;
END;
$$;

CREATE FUNCTION procrastinate_unlink_periodic_defers() RETURNS trigger
    LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE procrastinate_periodic_defers
    SET job_id = NULL
    WHERE job_id = OLD.id;
    RETURN OLD;
END;
$$;

-- Triggers

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

CREATE TRIGGER procrastinate_trigger_delete_jobs
    BEFORE DELETE ON procrastinate_jobs
    FOR EACH ROW EXECUTE PROCEDURE procrastinate_unlink_periodic_defers();


-- Old versions of functions, for backwards compatibility (to be removed
-- after 1.0.0)

CREATE FUNCTION procrastinate_finish_job(job_id integer, end_status procrastinate_job_status, next_scheduled_at timestamp with time zone) RETURNS void
    LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE procrastinate_jobs
    SET status = end_status,
        attempts = attempts + 1,
        scheduled_at = COALESCE(next_scheduled_at, scheduled_at)
    WHERE id = job_id;
END;
$$;

CREATE FUNCTION procrastinate_finish_job(job_id integer, end_status procrastinate_job_status) RETURNS void
    LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE procrastinate_jobs
    SET status = end_status,
        attempts = attempts + 1
    WHERE id = job_id;
END;
$$;

CREATE FUNCTION procrastinate_defer_periodic_job(
    _queue_name character varying,
    _lock character varying,
    _queueing_lock character varying,
    _task_name character varying,
    _defer_timestamp bigint
) RETURNS bigint
    LANGUAGE plpgsql
    AS $$
DECLARE
	_job_id bigint;
	_defer_id bigint;
BEGIN

    INSERT
        INTO procrastinate_periodic_defers (task_name, queue_name, defer_timestamp)
        VALUES (_task_name, _queue_name, _defer_timestamp)
        ON CONFLICT DO NOTHING
        RETURNING id into _defer_id;

    IF _defer_id IS NULL THEN
        RETURN NULL;
    END IF;

    UPDATE procrastinate_periodic_defers
        SET job_id = procrastinate_defer_job(
                _queue_name,
                _task_name,
                _lock,
                _queueing_lock,
                ('{"timestamp": ' || _defer_timestamp || '}')::jsonb,
                NULL
            )
        WHERE id = _defer_id
        RETURNING job_id INTO _job_id;

    DELETE
        FROM procrastinate_periodic_defers
        USING (
            SELECT id
            FROM procrastinate_periodic_defers
            WHERE procrastinate_periodic_defers.task_name = _task_name
            AND procrastinate_periodic_defers.queue_name = _queue_name
            AND procrastinate_periodic_defers.defer_timestamp < _defer_timestamp
            ORDER BY id
            FOR UPDATE
        ) to_delete
        WHERE procrastinate_periodic_defers.id = to_delete.id;

    RETURN _job_id;
END;
$$;
