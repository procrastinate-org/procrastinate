-- Drop the previous fetch_job function now that the upgraded code calls
-- procrastinate_fetch_job_v3.

DROP FUNCTION IF EXISTS procrastinate_fetch_job_v2(character varying[], bigint);
