import procrastinate

import_paths = ["procrastinate_demo.tasks"]
is_async = False  # set to True to run async demo
if is_async:
    connector_class = procrastinate.AiopgConnector
else:
    connector_class = procrastinate.Psycopg2Connector

app = procrastinate.App(
    connector=connector_class(),
    import_paths=import_paths,
    worker_defaults={"listen_notify": False},
)
app.open()
