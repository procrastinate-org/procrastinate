CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

CREATE TYPE public.cabbage_job_status AS ENUM (
    'todo',
    'doing',
    'done',
    'error'
);

CREATE TABLE public.cabbage_jobs (
    id integer NOT NULL,
    queue_name character varying(128) NOT NULL,
    task_name character varying(128) NOT NULL,
    lock text,
    args jsonb DEFAULT '{}' NOT NULL,
    status public.cabbage_job_status DEFAULT 'todo'::public.cabbage_job_status NOT NULL,
    scheduled_at timestamp with time zone NULL,
    started_at timestamp with time zone NULL,
    attempts integer DEFAULT 0 NOT NULL
);

CREATE UNLOGGED TABLE public.cabbage_job_locks (
    object text NOT NULL
);

CREATE FUNCTION public.cabbage_fetch_job(target_queue_names character varying[]) RETURNS public.cabbage_jobs
    LANGUAGE plpgsql
    AS $$
DECLARE
	found_jobs cabbage_jobs;
BEGIN
	WITH potential_job AS (
		SELECT cabbage_jobs.*
			FROM cabbage_jobs
			LEFT JOIN cabbage_job_locks ON cabbage_job_locks.object = cabbage_jobs.lock
			WHERE (target_queue_names IS NULL OR queue_name = ANY( target_queue_names ))
			  AND cabbage_job_locks.object IS NULL
			  AND status = 'todo'
			  AND (scheduled_at IS NULL OR scheduled_at <= now())
            ORDER BY id ASC
			FOR UPDATE OF cabbage_jobs SKIP LOCKED LIMIT 1
	), lock_object AS (
		INSERT INTO cabbage_job_locks
			SELECT lock FROM potential_job
	)
	UPDATE cabbage_jobs
		SET status = 'doing',
            started_at = NOW()
		FROM potential_job
		WHERE cabbage_jobs.id = potential_job.id
		RETURNING * INTO found_jobs;

	RETURN found_jobs;
END;
$$;

CREATE FUNCTION public.cabbage_finish_job(job_id integer, end_status public.cabbage_job_status, next_scheduled_at timestamp with time zone) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
	WITH finished_job AS (
		UPDATE cabbage_jobs
        SET status = end_status,
            attempts = attempts + 1,
            scheduled_at = COALESCE(next_scheduled_at, scheduled_at)
        WHERE id = job_id RETURNING lock
	)
	DELETE FROM cabbage_job_locks WHERE object = (SELECT lock FROM finished_job);
END;
$$;

CREATE FUNCTION public.cabbage_notify_queue() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	PERFORM pg_notify('cabbage_queue#' || NEW.queue_name, NEW.task_name);
	PERFORM pg_notify('cabbage_any_queue', NEW.task_name);
	RETURN NEW;
END;
$$;

CREATE SEQUENCE public.cabbage_jobs_id_seq;

ALTER SEQUENCE public.cabbage_jobs_id_seq OWNED BY public.cabbage_jobs.id;

ALTER TABLE ONLY public.cabbage_jobs ALTER COLUMN id
    SET DEFAULT nextval('public.cabbage_jobs_id_seq'::regclass);

ALTER TABLE ONLY public.cabbage_job_locks
    ADD CONSTRAINT cabbage_job_locks_object_key UNIQUE (object);

ALTER TABLE ONLY public.cabbage_jobs
    ADD CONSTRAINT cabbage_jobs_pkey PRIMARY KEY (id);

CREATE INDEX ON cabbage_jobs(queue_name);

CREATE TRIGGER cabbage_jobs_cabbage_notify_queue
    AFTER INSERT ON public.cabbage_jobs
    FOR EACH ROW WHEN ((new.status = 'todo'::public.cabbage_job_status))
    EXECUTE PROCEDURE public.cabbage_notify_queue();
