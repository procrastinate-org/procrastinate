import procrastinate

app = procrastinate.App(
    connector=procrastinate.AiopgConnector(), import_paths=["procrastinate_demo.tasks"],
)
