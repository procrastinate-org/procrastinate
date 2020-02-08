import procrastinate

app = procrastinate.App(
    connector=procrastinate.PostgresConnector(
        dsn="postgresql://postgres@localhost/procrastinate"
    ),
    import_paths=["procrastinate_demo.tasks"],
)
