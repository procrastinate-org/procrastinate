import procrastinate

app = procrastinate.App(
    connector=procrastinate.PostgresConnector(),
    import_paths=["procrastinate_demo.tasks"],
)
