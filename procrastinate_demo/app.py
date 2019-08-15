import procrastinate

app = procrastinate.App(
    job_store=procrastinate.PostgresJobStore(
        dsn="postgresql://postgres@localhost/procrastinate"
    ),
    import_paths=["procrastinate_demo.tasks"],
)
