import procrastinate

import_paths = ["procrastinate_demo.tasks"]

connector_class = procrastinate.Psycopg2Connector

app = procrastinate.App(connector=connector_class(), import_paths=import_paths)
app.open()
