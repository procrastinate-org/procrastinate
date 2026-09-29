-- add a deferred_at column to the procrastinate_jobs table
-- (added without a default first so that pre-existing jobs keep NULL
-- instead of being backfilled with the migration timestamp)
ALTER TABLE procrastinate_jobs ADD COLUMN deferred_at timestamp with time zone;
ALTER TABLE procrastinate_jobs ALTER COLUMN deferred_at SET DEFAULT NOW();
