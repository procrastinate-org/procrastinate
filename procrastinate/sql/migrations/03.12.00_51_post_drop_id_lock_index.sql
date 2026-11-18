-- Migration: Drop the (id, lock) index, replaced by procrastinate_jobs_todo_doing_lock_idx_v1
--
-- Since the outer scan of procrastinate_fetch_job_v2 uses procrastinate_jobs_priority_idx_v1,
-- the only use of this index was the lock check, which cannot seek on its second column.
-- Dropped concurrently so that queries on the table don't queue behind the drop:
-- this file must stay a single statement, run outside of a transaction.
DROP INDEX CONCURRENTLY IF EXISTS procrastinate_jobs_id_lock_idx_v1;
