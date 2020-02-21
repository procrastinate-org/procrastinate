import procrastinate

app = procrastinate.App(
    connector=procrastinate.PostgresConnector.create_with_pool(  # type: ignore
        dsn="postgresql://postgres@localhost/procrastinate"
    ),
    import_paths=["procrastinate_demo.tasks"],
)
