-- File format:
    -- query_name --
    -- description
    -- %s-templated QUERY

-- defer_job --
-- Create and enqueue a job
SELECT procrastinate_defer_job(%(queue)s, %(task_name)s, %(lock)s, %(queueing_lock)s, %(args)s, %(scheduled_at)s) AS id;

-- defer_periodic_job --
-- Create a periodic job if it doesn't already exist, and delete periodic metadata
-- for previous jobs in the same task.
SELECT procrastinate_defer_periodic_job(%(queue)s, %(lock)s, %(queueing_lock)s, %(task_name)s, %(periodic_id)s, %(defer_timestamp)s, %(args)s) AS id;

-- fetch_job --
-- Get the first awaiting job
SELECT id, status, task_name, lock, queueing_lock, args, scheduled_at, queue_name, attempts
    FROM procrastinate_fetch_job(%(queues)s);

-- select_stalled_jobs --
-- Get running jobs that started more than a given time ago
SELECT job.id, status, task_name, lock, queueing_lock, args, scheduled_at, queue_name, attempts, max(event.at) started_at
    FROM procrastinate_jobs job
    JOIN procrastinate_events event
      ON event.job_id = job.id
WHERE event.type = 'started'
  AND job.status = 'doing'
  AND event.at < NOW() - (%(nb_seconds)s || 'SECOND')::INTERVAL
  AND (%(queue)s IS NULL OR job.queue_name = %(queue)s)
  AND (%(task_name)s IS NULL OR job.task_name = %(task_name)s)
GROUP BY job.id

-- delete_old_jobs --
-- Delete jobs that have been in a final state for longer than nb_hours
DELETE FROM procrastinate_jobs
WHERE id IN (
    SELECT job.id FROM (
        SELECT DISTINCT ON (job.id) job.*, event.at AS latest_at
            FROM procrastinate_jobs job
            JOIN procrastinate_events event
              ON job.id = event.job_id
            ORDER BY job.id, event.at DESC
    ) AS job
    WHERE job.status in %(statuses)s
      AND (%(queue)s IS NULL OR job.queue_name = %(queue)s)
      AND latest_at < NOW() - (%(nb_hours)s || 'HOUR')::INTERVAL
)

-- finish_job --
-- Finish a job, changing it from "doing" to "succeeded" or "failed"
SELECT procrastinate_finish_job(%(job_id)s, %(status)s, NULL, %(delete_job)s);

-- retry_job --
-- Retry a job, changing it from "doing" to "todo"
SELECT procrastinate_retry_job(%(job_id)s, %(retry_at)s);

-- listen_queue --
-- In this one, the argument is an identifier, shoud not be escaped the same way
LISTEN {channel_name};

-- check_connection --
-- This query checks that the procrastinate_jobs table exists. Returns NULL otherwise.
SELECT to_regclass('procrastinate_jobs') as check;

-- count_jobs_status --
-- Count the number of jobs per status
SELECT count(*) AS count, status FROM procrastinate_jobs GROUP BY status;

-- list_jobs --
-- Get list of jobs
SELECT id,
       queue_name,
       task_name,
       lock,
       queueing_lock,
       args,
       status,
       scheduled_at,
       attempts
  FROM procrastinate_jobs
 WHERE (%(id)s IS NULL OR id = %(id)s)
   AND (%(queue_name)s IS NULL OR queue_name = %(queue_name)s)
   AND (%(task_name)s IS NULL OR task_name = %(task_name)s)
   AND (%(status)s IS NULL OR status = %(status)s)
   AND (%(lock)s IS NULL OR lock = %(lock)s)
   AND (%(queueing_lock)s IS NULL OR queueing_lock = %(queueing_lock)s)
 ORDER BY id ASC;

-- list_queues --
-- Get list of queues and number of jobs per queue
WITH jobs AS (
   SELECT id,
          queue_name,
          task_name,
          lock,
          args,
          status,
          scheduled_at,
          attempts
     FROM procrastinate_jobs
    WHERE (%(queue_name)s IS NULL OR queue_name = %(queue_name)s)
      AND (%(task_name)s IS NULL OR task_name = %(task_name)s)
      AND (%(status)s IS NULL OR status = %(status)s)
      AND (%(lock)s IS NULL OR lock = %(lock)s)
)
SELECT queue_name AS name,
       COUNT(id) AS jobs_count,
       (WITH stats AS (
           SELECT status,
                  COUNT(*) AS jobs_count
             FROM jobs
            WHERE queue_name = j.queue_name
            GROUP BY status
           )
           SELECT json_object_agg(status, jobs_count) FROM stats
       ) AS stats
  FROM jobs AS j
 GROUP BY name
 ORDER BY name;

-- list_tasks --
-- Get list of tasks and number of jobs per task
WITH jobs AS (
   SELECT id,
          queue_name,
          task_name,
          lock,
          args,
          status,
          scheduled_at,
          attempts
     FROM procrastinate_jobs
    WHERE (%(queue_name)s IS NULL OR queue_name = %(queue_name)s)
      AND (%(task_name)s IS NULL OR task_name = %(task_name)s)
      AND (%(status)s IS NULL OR status = %(status)s)
      AND (%(lock)s IS NULL OR lock = %(lock)s)
)
SELECT task_name AS name,
       COUNT(id) AS jobs_count,
       (WITH stats AS (
           SELECT status,
                  COUNT(*) AS jobs_count
             FROM jobs
            WHERE task_name = j.task_name
            GROUP BY status
           )
           SELECT json_object_agg(status, jobs_count) FROM stats
       ) AS stats
  FROM jobs AS j
 GROUP BY name
 ORDER BY name;

-- list_locks --
-- Get list of locks and number of jobs per lock
WITH jobs AS (
  SELECT
    id,
    lock,
    status
  FROM procrastinate_jobs
  WHERE (%(queue_name)s IS NULL OR queue_name = %(queue_name)s)
  AND (%(task_name)s IS NULL OR task_name = %(task_name)s)
  AND (%(status)s IS NULL OR status = %(status)s)
  AND (%(lock)s IS NULL OR lock = %(lock)s)
  AND lock IS NOT NULL
), locks AS (
  SELECT
    lock,
    status,
    count(id) AS jobs_count
  FROM jobs
  GROUP BY lock, status
)
SELECT
  lock AS name,
  sum(jobs_count) AS jobs_count,
  json_object_agg(status, jobs_count) AS stats
FROM locks
GROUP BY name
ORDER BY name;
