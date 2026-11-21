-- Migration: Drop procrastinate_retry_job_v2, superseded by procrastinate_retry_job_v3.
-- Safe to run once no old Procrastinate code (which calls it) is left.
DROP FUNCTION IF EXISTS procrastinate_retry_job_v2(bigint, timestamp with time zone, integer, character varying, character varying);
