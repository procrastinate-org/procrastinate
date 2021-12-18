ALTER TABLE procrastinate_periodic_defers
ADD IF NOT EXISTS name_suffix character varying(128) NOT NULL DEFAULT '';

ALTER TABLE procrastinate_periodic_defers
    DROP CONSTRAINT IF EXISTS procrastinate_periodic_defers_unique;

ALTER TABLE procrastinate_periodic_defers
    ADD CONSTRAINT procrastinate_periodic_defers_unique UNIQUE (task_name, name_suffix, queue_name, defer_timestamp);

CREATE FUNCTION procrastinate_defer_periodic_job(
    _queue_name character varying,
    _lock character varying,
    _queueing_lock character varying,
    _task_name character varying,
    _name_suffix character varying,
    _defer_timestamp bigint,
    _args jsonb
) RETURNS bigint
    LANGUAGE plpgsql
AS $$
DECLARE
	_job_id bigint;
	_defer_id bigint;
BEGIN

    INSERT
        INTO procrastinate_periodic_defers (task_name, name_suffix, queue_name, defer_timestamp)
        VALUES (_task_name, _name_suffix, _queue_name, _defer_timestamp)
        ON CONFLICT DO NOTHING
        RETURNING id into _defer_id;

    IF _defer_id IS NULL THEN
        RETURN NULL;
    END IF;

    UPDATE procrastinate_periodic_defers
        SET job_id = procrastinate_defer_job(
                _queue_name,
                _task_name,
                _lock,
                _queueing_lock,
                _args,
                NULL
            )
        WHERE id = _defer_id
        RETURNING job_id INTO _job_id;

    DELETE
        FROM procrastinate_periodic_defers
        USING (
            SELECT id
            FROM procrastinate_periodic_defers
            WHERE procrastinate_periodic_defers.task_name = _task_name
            AND procrastinate_periodic_defers.queue_name = _queue_name
            AND procrastinate_periodic_defers.defer_timestamp < _defer_timestamp
            ORDER BY id
            FOR UPDATE
        ) to_delete
        WHERE procrastinate_periodic_defers.id = to_delete.id;

    RETURN _job_id;
END;
$$;
