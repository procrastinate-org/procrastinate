-- Migration: remove the defer functions and composite type superseded by the lock_mode ones.
-- Safe to run once no old Procrastinate code (which calls procrastinate_defer_jobs_v1 or
-- procrastinate_defer_periodic_job_v2) is left.
DROP FUNCTION IF EXISTS procrastinate_defer_jobs_v1(jobs procrastinate_job_to_defer_v1[]);
DROP TYPE IF EXISTS procrastinate_job_to_defer_v1;
DROP FUNCTION IF EXISTS procrastinate_defer_periodic_job_v2(_queue_name character varying, _lock character varying, _queueing_lock character varying, _task_name character varying, _priority integer, _periodic_id character varying, _defer_timestamp bigint, _args jsonb);
