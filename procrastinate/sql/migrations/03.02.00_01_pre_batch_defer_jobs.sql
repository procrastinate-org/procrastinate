CREATE FUNCTION procrastinate_defer_jobs_v1(
    queue_names character varying[],
    task_names character varying[],
    priorities integer[],
    locks text[],
    queueing_locks text[],
    args_list jsonb[],
    scheduled_ats timestamp with time zone[]
)
    RETURNS bigint[]
    LANGUAGE plpgsql
AS $$
DECLARE
    job_ids bigint[];
    array_length integer;
    i integer;
BEGIN
    array_length := array_length(queue_names, 1);
    IF array_length != array_length(task_names, 1) OR
       array_length != array_length(priorities, 1) OR
       array_length != array_length(locks, 1) OR
       array_length != array_length(queueing_locks, 1) OR
       array_length != array_length(args_list, 1) OR
       array_length != array_length(scheduled_ats, 1) THEN
        RAISE EXCEPTION 'All input arrays must have the same length';
    END IF;

    job_ids := ARRAY[]::bigint[];
    WITH inserted_jobs AS (
        INSERT INTO procrastinate_jobs (queue_name, task_name, priority, lock, queueing_lock, args, scheduled_at)
        SELECT unnest(queue_names),
               unnest(task_names),
               unnest(priorities),
               unnest(locks),
               unnest(queueing_locks),
               unnest(args_list),
               unnest(scheduled_ats)
        RETURNING id
    )
    SELECT array_agg(id) FROM inserted_jobs INTO job_ids;

    RETURN job_ids;
END;
$$;

CREATE FUNCTION procrastinate_defer_periodic_job_v2(
    _queue_name character varying,
    _lock character varying,
    _queueing_lock character varying,
    _task_name character varying,
    _priority integer,
    _periodic_id character varying,
    _defer_timestamp bigint,
    _args jsonb
)
    RETURNS bigint
    LANGUAGE plpgsql
AS $$
DECLARE
	_job_id bigint;
	_defer_id bigint;
BEGIN

    INSERT
        INTO procrastinate_periodic_defers (task_name, periodic_id, defer_timestamp)
        VALUES (_task_name, _periodic_id, _defer_timestamp)
        ON CONFLICT DO NOTHING
        RETURNING id into _defer_id;

    IF _defer_id IS NULL THEN
        RETURN NULL;
    END IF;

    UPDATE procrastinate_periodic_defers
        SET job_id = (
            SELECT COALESCE((
                SELECT unnest(procrastinate_defer_jobs_v1(
                    ARRAY[_queue_name]::character varying[],
                    ARRAY[_task_name]::character varying[],
                    ARRAY[_priority]::integer[],
                    ARRAY[_lock]::text[],
                    ARRAY[_queueing_lock]::text[],
                    ARRAY[_args]::jsonb[],
                    ARRAY[NULL::timestamptz]
                ))
            ), NULL)
        )
        WHERE id = _defer_id
        RETURNING job_id INTO _job_id;

    DELETE
        FROM procrastinate_periodic_defers
        USING (
            SELECT id
            FROM procrastinate_periodic_defers
            WHERE procrastinate_periodic_defers.task_name = _task_name
            AND procrastinate_periodic_defers.periodic_id = _periodic_id
            AND procrastinate_periodic_defers.defer_timestamp < _defer_timestamp
            ORDER BY id
            FOR UPDATE
        ) to_delete
        WHERE procrastinate_periodic_defers.id = to_delete.id;

    RETURN _job_id;
END;
$$;
