-- Migration: add a lock_mode to jobs, so that a lock can provide mutual exclusion
-- without also providing ordering.
--
-- 'ordered' (the default, and the pre-existing behaviour) keeps reserving the lock while
-- a job is merely waiting, which is what guarantees jobs sharing a lock start in order.
-- 'mutex' only reserves the lock while a job is actually running, so a job that is not
-- runnable yet (e.g. a long retry backoff) no longer holds up other jobs on that lock.

CREATE TYPE procrastinate_lock_mode AS ENUM (
    'ordered',  -- A waiting job holds the lock even when it cannot run yet
    'mutex'  -- A job only holds the lock while it is runnable
);

ALTER TABLE procrastinate_jobs
    ADD COLUMN lock_mode procrastinate_lock_mode DEFAULT 'ordered' NOT NULL;

CREATE TYPE procrastinate_job_to_defer_v2 AS (
    queue_name character varying,
    task_name character varying,
    priority integer,
    lock text,
    queueing_lock text,
    args jsonb,
    scheduled_at timestamp with time zone,
    lock_mode procrastinate_lock_mode
);

CREATE FUNCTION procrastinate_defer_jobs_v2(
    jobs procrastinate_job_to_defer_v2[]
)
    RETURNS bigint[]
    LANGUAGE plpgsql
AS $$
DECLARE
    job_ids bigint[];
BEGIN
    WITH inserted_jobs AS (
        INSERT INTO procrastinate_jobs (queue_name, task_name, priority, lock, lock_mode, queueing_lock, args, scheduled_at)
        SELECT (job).queue_name,
               (job).task_name,
               (job).priority,
               (job).lock,
               COALESCE((job).lock_mode, 'ordered'),
               (job).queueing_lock,
               (job).args,
               (job).scheduled_at
        FROM unnest(jobs) AS job
        RETURNING id
    )
    SELECT array_agg(id) FROM inserted_jobs INTO job_ids;

    RETURN job_ids;
END;
$$;

CREATE OR REPLACE FUNCTION procrastinate_defer_periodic_job_v2(
    _queue_name character varying,
    _lock character varying,
    _queueing_lock character varying,
    _task_name character varying,
    _priority integer,
    _periodic_id character varying,
    _defer_timestamp bigint,
    _args jsonb
)
    RETURNS bigint
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
        SET job_id = (
            SELECT COALESCE((
                SELECT unnest(procrastinate_defer_jobs_v2(
                    ARRAY[
                        ROW(
                            _queue_name,
                            _task_name,
                            _priority,
                            _lock,
                            _queueing_lock,
                            _args,
                            NULL::timestamptz,
                            'ordered'::procrastinate_lock_mode
                        )
                    ]::procrastinate_job_to_defer_v2[]
                ))
            ), NULL)
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

-- v2 is kept above so code still running during the upgrade keeps working;
-- it is dropped in the matching post-migration.
CREATE FUNCTION procrastinate_defer_periodic_job_v3(
    _queue_name character varying,
    _lock character varying,
    _lock_mode procrastinate_lock_mode,
    _queueing_lock character varying,
    _task_name character varying,
    _priority integer,
    _periodic_id character varying,
    _defer_timestamp bigint,
    _args jsonb
)
    RETURNS bigint
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
        SET job_id = (
            SELECT COALESCE((
                SELECT unnest(procrastinate_defer_jobs_v2(
                    ARRAY[
                        ROW(
                            _queue_name,
                            _task_name,
                            _priority,
                            _lock,
                            _queueing_lock,
                            _args,
                            NULL::timestamptz,
                            COALESCE(_lock_mode, 'ordered')
                        )
                    ]::procrastinate_job_to_defer_v2[]
                ))
            ), NULL)
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

CREATE OR REPLACE FUNCTION procrastinate_fetch_job_v2(
    target_queue_names character varying[],
    p_worker_id bigint
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
                -- reject the job if its lock has earlier or higher priority jobs.
                -- Jobs without a lock are accepted before the subquery is considered:
                -- keeping "jobs.lock IS NOT NULL" inside the subquery lets Postgres
                -- plan a nested loop that scans every other job for each NULL-lock job.
                (
                    jobs.lock IS NULL
                    OR NOT EXISTS (
                        SELECT 1
                            FROM procrastinate_jobs AS other_jobs
                            WHERE
                                other_jobs.lock = jobs.lock
                                AND (
                                    -- job with same lock is already running
                                    other_jobs.status = 'doing'
                                    OR
                                    -- job with same lock is waiting and has higher priority (or same priority but was queued first).
                                    -- A waiting 'mutex' job only counts once it is due, so a job scheduled for later steps
                                    -- aside; an 'ordered' job always counts, which keeps the jobs sharing its lock in order.
                                    -- Workers fetching as a 'mutex' job becomes due can disagree on this, as now() differs
                                    -- per transaction, and pick two jobs sharing a lock: procrastinate_jobs_lock_idx_v1
                                    -- then refuses the second one, which the caller treats as finding no job.
                                    (
                                        other_jobs.status = 'todo'
                                        AND (
                                            other_jobs.lock_mode = 'ordered'
                                            OR other_jobs.scheduled_at IS NULL
                                            OR other_jobs.scheduled_at <= now()
                                        )
                                        AND (
                                            other_jobs.priority > jobs.priority
                                            OR (
                                            other_jobs.priority = jobs.priority
                                            AND other_jobs.id < jobs.id
                                            )
                                        )
                                    )
                                )
                    )
                )
                AND jobs.status = 'todo'
                AND (target_queue_names IS NULL OR jobs.queue_name = ANY( target_queue_names ))
                AND (jobs.scheduled_at IS NULL OR jobs.scheduled_at <= now())
            ORDER BY jobs.priority DESC, jobs.id ASC LIMIT 1
            FOR UPDATE OF jobs SKIP LOCKED
    )
    UPDATE procrastinate_jobs
        SET status = 'doing', worker_id = p_worker_id
        FROM candidate
        WHERE procrastinate_jobs.id = candidate.id
        RETURNING procrastinate_jobs.* INTO found_jobs;

 RETURN found_jobs;
END;
$$;
