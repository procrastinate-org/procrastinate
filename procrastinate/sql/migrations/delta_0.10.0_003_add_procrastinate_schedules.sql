CREATE TABLE procrastinate_schedules (
    id bigserial PRIMARY KEY,
    task_name character varying(128) NOT NULL,
    schedule_timestamp bigint,
    job_id bigint REFERENCES procrastinate_jobs(id) NULL,
    UNIQUE (task_name, schedule_timestamp)
);

-- When parameters change, function must be dropped.
DROP FUNCTION procrastinate_defer_job;
CREATE OR REPLACE FUNCTION procrastinate_defer_job(
    queue_name character varying,
    task_name character varying,
    lock text,
    queueing_lock text,
    args jsonb,
    scheduled_at timestamp with time zone
) RETURNS bigint
    LANGUAGE plpgsql
    AS $$
DECLARE
	job_id bigint;
BEGIN
    INSERT INTO procrastinate_jobs (queue_name, task_name, lock, queueing_lock, args, scheduled_at)
    VALUES (queue_name, task_name, lock, queueing_lock, args, scheduled_at)
    RETURNING id INTO job_id;

    RETURN job_id;
END;
$$;

CREATE OR REPLACE FUNCTION procrastinate_defer_periodic_job(
    _queue_name character varying,
    _task_name character varying,
    _schedule_timestamp bigint
) RETURNS bigint
    LANGUAGE plpgsql
    AS $$
DECLARE
	periodic_job_id bigint;
	schedule_id bigint;
BEGIN

    INSERT
        INTO procrastinate_schedules (task_name, schedule_timestamp)
        VALUES (_task_name, _schedule_timestamp)
        ON CONFLICT DO NOTHING
        RETURNING id into schedule_id;

    IF schedule_id IS NULL THEN
        RETURN NULL;
    END IF;

    UPDATE procrastinate_schedules
        SET job_id = procrastinate_defer_job(
                _queue_name,
                _task_name,
                NULL,
                NULL,
                ('{"timestamp": ' || _schedule_timestamp || '}')::jsonb,
                NULL
            )
        WHERE id = schedule_id
        RETURNING job_id INTO periodic_job_id;

    DELETE
        FROM procrastinate_schedules
        WHERE
            periodic_job_id IS NOT NULL
            AND procrastinate_schedules.task_name = _task_name
            AND procrastinate_schedules.schedule_timestamp < _schedule_timestamp;

    RETURN periodic_job_id;
END;
$$;
