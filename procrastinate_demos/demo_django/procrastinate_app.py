import procrastinate

app = procrastinate.App(
    connector=procrastinate.PsycopgConnector(),
    import_paths=[
        "procrastinate_demos.demo_django.demo.tasks",
    ],
)
