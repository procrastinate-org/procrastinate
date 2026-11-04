-- Add index on queue_name for better performance when querying jobs by queue
CREATE INDEX IF NOT EXISTS procrastinate_jobs_queue_name_idx ON procrastinate_jobs(queue_name);
