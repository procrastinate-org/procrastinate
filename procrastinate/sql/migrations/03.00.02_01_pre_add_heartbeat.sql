CREATE TABLE procrastinate_worker_heartbeats(
    id bigserial PRIMARY KEY,
    worker_id character varying(36) NOT NULL UNIQUE,
    last_heartbeat timestamp with time zone NOT NULL DEFAULT NOW()
);

CREATE FUNCTION procrastinate_update_heartbeat_v1(p_worker_id character varying)
    RETURNS void
    LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO procrastinate_worker_heartbeats(worker_id)
    VALUES (p_worker_id)
    ON CONFLICT (worker_id)
    DO UPDATE SET last_heartbeat = NOW();
END;
$$;

CREATE FUNCTION procrastinate_delete_heartbeat_v1(p_worker_id character varying)
    RETURNS void
    LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM procrastinate_worker_heartbeats
    WHERE worker_id = p_worker_id;
END;
$$;

ALTER TABLE procrastinate_jobs ADD COLUMN worker_id character varying(36) NULL;

CREATE FUNCTION procrastinate_fetch_job_v2(
    target_queue_names character varying[],
    p_worker_id character varying
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
        SET status = 'doing', worker_id = p_worker_id
        FROM candidate
        WHERE procrastinate_jobs.id = candidate.id
        RETURNING procrastinate_jobs.* INTO found_jobs;

	RETURN found_jobs;
END;
$$;
