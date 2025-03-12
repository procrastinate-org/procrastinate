CREATE TABLE procrastinate_worker_heartbeats(
    id bigserial PRIMARY KEY,
    worker_id character varying(36) NOT NULL UNIQUE,
    last_heartbeat timestamp with time zone NOT NULL DEFAULT NOW()
);

CREATE FUNCTION procrastinate_update_heartbeat_v1(p_worker_id character varying)
    RETURNS void
    LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO procrastinate_worker_heartbeats(worker_id)
    VALUES (p_worker_id)
    ON CONFLICT (worker_id)
    DO UPDATE SET last_heartbeat = NOW();
END;
$$;

CREATE FUNCTION procrastinate_delete_heartbeat_v1(p_worker_id character varying)
    RETURNS void
    LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM procrastinate_worker_heartbeats
    WHERE worker_id = p_worker_id;
END;
$$;
