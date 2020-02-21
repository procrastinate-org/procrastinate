-- File format:
    -- query_name --
    -- description
    -- %s-templated QUERY

-- defer_job --
-- Create and enqueue a job
INSERT INTO procrastinate_jobs (queue_name, task_name, lock, args, scheduled_at)
VALUES (%(queue)s, %(task_name)s, %(lock)s, %(args)s, %(scheduled_at)s)
RETURNING id;

-- fetch_job --
-- Get the first awaiting job
SELECT id, task_name, lock, args, scheduled_at, queue_name, attempts
    FROM procrastinate_fetch_job(%(queues)s);

-- select_stalled_jobs --
-- Get running jobs that started more than a given time ago
SELECT job.id, task_name, lock, args, scheduled_at, queue_name, attempts, max(event.at) started_at
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
