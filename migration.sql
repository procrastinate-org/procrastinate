--
-- PostgreSQL database dump
--

-- Dumped from database version 10.6 (Debian 10.6-1.pgdg100+1+b1)
-- Dumped by pg_dump version 10.6 (Debian 10.6-1.pgdg100+1+b1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner:
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: hstore; Type: EXTENSION; Schema: -; Owner:
--

CREATE EXTENSION IF NOT EXISTS hstore WITH SCHEMA public;


--
-- Name: EXTENSION hstore; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION hstore IS 'data type for storing sets of (key, value) pairs';


--
-- Name: task_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.task_status AS ENUM (
    'todo',
    'doing',
    'done'
);


ALTER TYPE public.task_status OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    queue_id integer NOT NULL,
    task_type character varying(32) NOT NULL,
    targeted_object text,
    args jsonb DEFAULT '{}' NOT NULL,
    status public.task_status DEFAULT 'todo'::public.task_status NOT NULL
);


ALTER TABLE public.tasks OWNER TO postgres;

--
-- Name: fetch_task(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fetch_task(target_queue_name character varying) RETURNS public.tasks
    LANGUAGE plpgsql
    AS $$
DECLARE
	target_queue_id integer;
	found_task tasks;
BEGIN
	SELECT id INTO target_queue_id FROM queues WHERE queue_name = target_queue_name;

	-- Lock the queue. Could be done with a FOR UPDATE btw...
	PERFORM pg_advisory_lock(target_queue_id);

	WITH potential_task AS (
		SELECT tasks.*
			FROM tasks
			LEFT JOIN task_locks ON task_locks.object = tasks.targeted_object
			WHERE queue_id = target_queue_id AND task_locks.object IS NULL AND status = 'todo'
			FOR UPDATE OF tasks SKIP LOCKED LIMIT 1
	), lock_object AS (
		INSERT INTO task_locks
			SELECT targeted_object FROM potential_task
	)
	UPDATE tasks
		SET status = 'doing'
		FROM potential_task
		WHERE tasks.id = potential_task.id
		RETURNING * INTO found_task;

	PERFORM pg_advisory_unlock(target_queue_id);

	RETURN found_task;
END;
$$;


ALTER FUNCTION public.fetch_task(target_queue_name character varying) OWNER TO postgres;

--
-- Name: finish_task(integer, public.task_status); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.finish_task(task_id integer, end_status public.task_status) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
	target_queue_id integer;
BEGIN
	SELECT queue_id INTO target_queue_id FROM tasks WHERE id = task_id;

	PERFORM pg_advisory_lock(target_queue_id);

	WITH close_task AS (
		UPDATE tasks SET status = end_status WHERE id = task_id RETURNING targeted_object
	)
	DELETE FROM task_locks WHERE object = (SELECT targeted_object FROM close_task);

	PERFORM pg_advisory_unlock(target_queue_id);
END;
$$;


ALTER FUNCTION public.finish_task(task_id integer, end_status public.task_status) OWNER TO postgres;

--
-- Name: notify_queue(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.notify_queue() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	PERFORM pg_notify('queue#' || queue_name, NEW.task_type) FROM queues WHERE id = NEW.queue_id;
	RETURN NEW;
END;
$$;


ALTER FUNCTION public.notify_queue() OWNER TO postgres;

--
-- Name: queues; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.queues (
    id integer NOT NULL,
    queue_name character varying(32) UNIQUE
);


ALTER TABLE public.queues OWNER TO postgres;

--
-- Name: queues_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.queues_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.queues_id_seq OWNER TO postgres;

--
-- Name: queues_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.queues_id_seq OWNED BY public.queues.id;


--
-- Name: task_locks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE public.task_locks (
    object text NOT NULL
);


ALTER TABLE public.task_locks OWNER TO postgres;

--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tasks_id_seq OWNER TO postgres;

--
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- Name: queues id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queues ALTER COLUMN id SET DEFAULT nextval('public.queues_id_seq'::regclass);


--
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- Data for Name: queues; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.queues (id, queue_name) FROM stdin;
\.


--
-- Data for Name: task_locks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task_locks (object) FROM stdin;
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (id, queue_id, task_type, targeted_object, status) FROM stdin;
\.


--
-- Name: queues_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.queues_id_seq', 2, true);


--
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tasks_id_seq', 5, true);


--
-- Name: queues queues_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queues
    ADD CONSTRAINT queues_pkey PRIMARY KEY (id);


--
-- Name: task_locks task_locks_object_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_locks
    ADD CONSTRAINT task_locks_object_key UNIQUE (object);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_notify_queue; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tasks_notify_queue AFTER INSERT ON public.tasks FOR EACH ROW WHEN ((new.status = 'todo'::public.task_status)) EXECUTE PROCEDURE public.notify_queue();


--
-- Name: tasks tasks_queue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_queue_id_fkey FOREIGN KEY (queue_id) REFERENCES public.queues(id);


--
-- PostgreSQL database dump complete
--
