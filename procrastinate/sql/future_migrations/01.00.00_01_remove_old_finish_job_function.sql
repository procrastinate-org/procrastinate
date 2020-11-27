-- remove old procrastinate_finish_job functions
-- https://github.com/peopledoc/procrastinate/pull/336
DROP FUNCTION IF EXISTS procrastinate_finish_job(integer, procrastinate_job_status, timestamp with time zone);
-- https://github.com/peopledoc/procrastinate/pull/354
DROP FUNCTION IF EXISTS procrastinate_finish_job(integer, procrastinate_job_status);
