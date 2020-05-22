-- add a defer_lock column to the procrastinate_jobs table
ALTER TABLE procrastinate_jobs ADD COLUMN defer_lock text;
ALTER TABLE procrastinate_jobs ADD EXCLUDE (defer_lock WITH =, status WITH =) WHERE (status = 'todo');
