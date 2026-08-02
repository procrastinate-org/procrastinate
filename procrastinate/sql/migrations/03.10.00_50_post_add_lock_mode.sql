-- Migration: remove the defer function and composite type superseded by the lock_mode ones.
-- Safe to run once no old Procrastinate code (which calls procrastinate_defer_jobs_v1) is left.
DROP FUNCTION IF EXISTS procrastinate_defer_jobs_v1(jobs procrastinate_job_to_defer_v1[]);
DROP TYPE IF EXISTS procrastinate_job_to_defer_v1;
