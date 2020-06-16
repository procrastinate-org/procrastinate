import procrastinate

import_paths = ["procrastinate_demo.tasks"]

app = procrastinate.App(
    connector=procrastinate.AiopgConnector(), import_paths=import_paths
)

sync_app = procrastinate.App(
    connector=procrastinate.Psycopg2Connector(), import_paths=import_paths
)
