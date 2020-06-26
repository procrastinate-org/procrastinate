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
SELECT procrastinate_defer_periodic_job(%(queue)s, %(task_name)s, %(defer_timestamp)s) AS id;

-- fetch_job --
-- Get the first awaiting job
SELECT id, task_name, lock, queueing_lock, args, scheduled_at, queue_name, attempts
    FROM procrastinate_fetch_job(%(queues)s);

-- select_stalled_jobs --
-- Get running jobs that started more than a given time ago
SELECT job.id, task_name, lock, queueing_lock, args, scheduled_at, queue_name, attempts, max(event.at) started_at
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
-- Stop a job, free the lock and record the relevant events
SELECT procrastinate_finish_job(%(job_id)s, %(status)s, %(scheduled_at)s);

-- listen_queue --
-- In this one, the argument is an identifier, shoud not be escaped the same way
LISTEN {channel_name};

-- check_connection --
-- This does only check you have read permission
SELECT TRUE as check;

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

-- set_job_status --
UPDATE procrastinate_jobs
   SET status = %(status)s
 WHERE id = %(id)s
