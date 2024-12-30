-- new fetch job. Only checks for doing. On update conflict return NULL
CREATE OR REPLACE FUNCTION procrastinate.procrastinate_fetch_job(target_queue_names character varying[])
 RETURNS procrastinate.procrastinate_jobs
 LANGUAGE plpgsql
AS $function$
DECLARE
    found_jobs procrastinate_jobs;
    retry_count INT := 0;
BEGIN
    LOOP
        BEGIN
            WITH candidate AS (
                SELECT jobs.*
                FROM procrastinate_jobs AS jobs
                WHERE
                    (jobs.lock IS NULL OR
                    NOT EXISTS ( -- reject the job if its lock has current jobs
                        SELECT 1
                        FROM procrastinate_jobs AS jobs_with_locks
                        WHERE
                            jobs.lock IS NOT NULL
                            AND jobs_with_locks.lock = jobs.lock
                            AND jobs_with_locks.status = 'doing'
                            LIMIT 1
                    ))
                    AND jobs.status = 'todo'
                    AND (target_queue_names IS NULL OR jobs.queue_name = ANY(target_queue_names))
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
        EXCEPTION
            WHEN unique_violation THEN
                PERFORM pg_sleep(random() * 0.01); -- fuzzy retry with upto 10ms sleep
                retry_count := retry_count + 1;
                IF retry_count >= 3 THEN
                    RAISE; --reraise
                END IF;
        END;
    END LOOP;
END;
$function$
;

CREATE OR REPLACE FUNCTION procrastinate.procrastinate_fetch_job_without_lock(target_queue_names character varying[])
 RETURNS procrastinate.procrastinate_jobs
 LANGUAGE plpgsql
AS $$
DECLARE
    found_jobs procrastinate_jobs;
BEGIN
    WITH candidate AS (
        SELECT jobs.*
        FROM procrastinate_jobs AS jobs
        WHERE
            jobs.lock IS NULL
            AND jobs.status = 'todo'
            AND (target_queue_names IS NULL OR jobs.queue_name = ANY(target_queue_names))
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
