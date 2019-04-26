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
-- Name: cabbage_job_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.cabbage_job_status AS ENUM (
    'todo',
    'doing',
    'done',
    'error'
);


ALTER TYPE public.cabbage_job_status OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: cabbage_jobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cabbage_jobs (
    id integer NOT NULL,
    queue_id integer NOT NULL,
    task_name character varying(32) NOT NULL,
    lock text,
    args jsonb DEFAULT '{}' NOT NULL,
    status public.cabbage_job_status DEFAULT 'todo'::public.cabbage_job_status NOT NULL
);


ALTER TABLE public.cabbage_jobs OWNER TO postgres;

--
-- Name: cabbage_fetch_job(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.cabbage_fetch_job(target_queue_name character varying) RETURNS public.cabbage_jobs
    LANGUAGE plpgsql
    AS $$
DECLARE
	target_queue_id integer;
	found_jobs cabbage_jobs;
BEGIN
	SELECT id INTO target_queue_id FROM cabbage_queues WHERE queue_name = target_queue_name FOR UPDATE;

	WITH potential_job AS (
		SELECT cabbage_jobs.*
			FROM cabbage_jobs
			LEFT JOIN cabbage_job_locks ON cabbage_job_locks.object = cabbage_jobs.lock
			WHERE queue_id = target_queue_id AND cabbage_job_locks.object IS NULL AND status = 'todo'
			FOR UPDATE OF cabbage_jobs SKIP LOCKED LIMIT 1
	), lock_object AS (
		INSERT INTO cabbage_job_locks
			SELECT lock FROM potential_job
	)
	UPDATE cabbage_jobs
		SET status = 'doing'
		FROM potential_job
		WHERE cabbage_jobs.id = potential_job.id
		RETURNING * INTO found_jobs;

	RETURN found_jobs;
END;
$$;


ALTER FUNCTION public.cabbage_fetch_job(target_queue_name character varying) OWNER TO postgres;

--
-- Name: cabbage_finish_job(integer, public.cabbage_job_status); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.cabbage_finish_job(job_id integer, end_status public.cabbage_job_status) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
	target_queue_id integer;
BEGIN
	SELECT queue_id INTO target_queue_id FROM cabbage_jobs WHERE id = job_id;

	PERFORM pg_advisory_lock(target_queue_id);

	WITH finished_job AS (
		UPDATE cabbage_jobs SET status = end_status WHERE id = job_id RETURNING lock
	)
	DELETE FROM cabbage_job_locks WHERE object = (SELECT lock FROM finished_job);

	PERFORM pg_advisory_unlock(target_queue_id);
END;
$$;


ALTER FUNCTION public.cabbage_finish_job(job_id integer, end_status public.cabbage_job_status) OWNER TO postgres;

--
-- Name: cabbage_notify_queue(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.cabbage_notify_queue() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	PERFORM pg_notify('cabbage_queue#' || queue_name, NEW.task_name) FROM cabbage_queues WHERE id = NEW.queue_id;
	RETURN NEW;
END;
$$;


ALTER FUNCTION public.cabbage_notify_queue() OWNER TO postgres;

--
-- Name: cabbage_queues; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cabbage_queues (
    id integer NOT NULL,
    queue_name character varying(32) UNIQUE
);


ALTER TABLE public.cabbage_queues OWNER TO postgres;

--
-- Name: cabbage_queues_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cabbage_queues_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cabbage_queues_id_seq OWNER TO postgres;

--
-- Name: cabbage_queues_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cabbage_queues_id_seq OWNED BY public.cabbage_queues.id;


--
-- Name: cabbage_job_locks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE UNLOGGED TABLE public.cabbage_job_locks (
    object text NOT NULL
);


ALTER TABLE public.cabbage_job_locks OWNER TO postgres;

--
-- Name: cabbage_jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cabbage_jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cabbage_jobs_id_seq OWNER TO postgres;

--
-- Name: cabbage_jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cabbage_jobs_id_seq OWNED BY public.cabbage_jobs.id;


--
-- Name: cabbage_queues id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cabbage_queues ALTER COLUMN id SET DEFAULT nextval('public.cabbage_queues_id_seq'::regclass);


--
-- Name: cabbage_jobs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cabbage_jobs ALTER COLUMN id SET DEFAULT nextval('public.cabbage_jobs_id_seq'::regclass);

--
-- Name: cabbage_queues_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cabbage_queues_id_seq', 2, true);


--
-- Name: cabbage_jobs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cabbage_jobs_id_seq', 5, true);


--
-- Name: cabbage_queues cabbage_queues_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cabbage_queues
    ADD CONSTRAINT cabbage_queues_pkey PRIMARY KEY (id);


--
-- Name: cabbage_job_locks cabbage_job_locks_object_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cabbage_job_locks
    ADD CONSTRAINT cabbage_job_locks_object_key UNIQUE (object);


--
-- Name: cabbage_jobs cabbage_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cabbage_jobs
    ADD CONSTRAINT cabbage_jobs_pkey PRIMARY KEY (id);


--
-- Name: cabbage_jobs cabbage_jobs_cabbage_notify_queue; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER cabbage_jobs_cabbage_notify_queue AFTER INSERT ON public.cabbage_jobs FOR EACH ROW WHEN ((new.status = 'todo'::public.cabbage_job_status)) EXECUTE PROCEDURE public.cabbage_notify_queue();


--
-- Name: cabbage_jobs cabbage_jobs_queue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cabbage_jobs
    ADD CONSTRAINT cabbage_jobs_queue_id_fkey FOREIGN KEY (queue_id) REFERENCES public.cabbage_queues(id);


--
-- PostgreSQL database dump complete
--
