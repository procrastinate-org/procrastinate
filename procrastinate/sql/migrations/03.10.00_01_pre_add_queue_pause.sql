CREATE TABLE procrastinate_paused_queues (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    queue_name character varying(128) NOT NULL,
    pause_key character varying(128) DEFAULT 'default' NOT NULL,
    paused_at timestamp with time zone DEFAULT NOW() NOT NULL,
    UNIQUE (queue_name, pause_key)
);

CREATE FUNCTION procrastinate_fetch_job_v3(
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
                -- reject the job if its lock has earlier or higher priority jobs
                NOT EXISTS (
                    SELECT 1
                        FROM procrastinate_jobs AS other_jobs
                        WHERE
                            jobs.lock IS NOT NULL
                            AND other_jobs.lock = jobs.lock
                            AND (
                                -- job with same lock is already running
                                other_jobs.status = 'doing'
                                OR
                                -- job with same lock is waiting and has higher priority (or same priority but was queued first)
                                (
                                    other_jobs.status = 'todo'
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
                AND jobs.status = 'todo'
                AND (target_queue_names IS NULL OR jobs.queue_name = ANY( target_queue_names ))
                AND (jobs.scheduled_at IS NULL OR jobs.scheduled_at <= now())
                -- reject the job if its queue is paused
                AND NOT EXISTS (
                    SELECT 1
                        FROM procrastinate_paused_queues AS paused
                        WHERE paused.queue_name = jobs.queue_name
                )
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

CREATE FUNCTION procrastinate_notify_queue_resumed_v1()
    RETURNS trigger
    LANGUAGE plpgsql
AS $$
DECLARE
    payload TEXT;
BEGIN
    SELECT json_build_object('type', 'queue_resumed', 'queue_name', OLD.queue_name)::text INTO payload;
    PERFORM pg_notify('procrastinate_queue_v1#' || OLD.queue_name, payload);
    PERFORM pg_notify('procrastinate_any_queue_v1', payload);
    RETURN OLD;
END;
$$;

CREATE TRIGGER procrastinate_paused_queues_notify_queue_resumed_v1
    AFTER DELETE ON procrastinate_paused_queues
    FOR EACH ROW
    EXECUTE PROCEDURE procrastinate_notify_queue_resumed_v1();
