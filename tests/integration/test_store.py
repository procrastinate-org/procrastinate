def test_execute_query(pg_job_store):
    pg_job_store.execute_query("COMMENT ON TABLE \"procrastinate_jobs\" IS 'foo' ")

    with pg_job_store.connection.cursor() as cursor:
        cursor.execute("SELECT obj_description('public.procrastinate_jobs'::regclass)")
        assert cursor.fetchone()[0] == "foo"
