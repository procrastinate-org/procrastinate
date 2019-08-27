def test_execute_queries(pg_job_store):
    pg_job_store.execute_queries("COMMENT ON TABLE \"procrastinate_jobs\" IS 'foo' ")

    with pg_job_store.connection.cursor() as cursor:
        cursor.execute("SELECT obj_description('public.procrastinate_jobs'::regclass)")
        assert cursor.fetchone()[0] == "foo"
