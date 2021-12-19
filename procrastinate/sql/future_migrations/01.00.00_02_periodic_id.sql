
-- https://github.com/procrastinate-org/procrastinate/pull/471
DROP FUNCTION IF EXISTS procrastinate_defer_periodic_job(character varying, character varying, character varying, character varying, bigint);

ALTER TABLE procrastinate_periodic_defers
    DROP COLUMN "queue_name";
