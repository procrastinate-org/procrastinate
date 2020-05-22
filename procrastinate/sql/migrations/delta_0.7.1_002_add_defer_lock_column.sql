-- add a defer_lock column to the procrastinate_jobs table
ALTER TABLE procrastinate_jobs ADD COLUMN defer_lock text;
CREATE UNIQUE INDEX procrastinate_jobs_defer_lock_idx ON procrastinate_jobs (defer_lock) WHERE status = 'todo';
