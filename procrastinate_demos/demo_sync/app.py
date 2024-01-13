from __future__ import annotations

import procrastinate

app = procrastinate.App(
    connector=procrastinate.PsycopgConnector(),
    import_paths=["procrastinate_demos.demo_sync.tasks"],
)
