-- remove old procrastinate_finish_job function
-- https://github.com/peopledoc/procrastinate/pull/336
DROP FUNCTION IF EXISTS procrastinate_finish_job(integer, procrastinate_job_status, timestamp with time zone);
