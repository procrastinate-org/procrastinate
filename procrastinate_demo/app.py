import os

import procrastinate

DSN = os.environ.get(
    "PROCRASTINATE_POSTGRES_DSN", "postgresql://postgres@localhost/procrastinate"
)
app = procrastinate.App(
    job_store=procrastinate.PostgresJobStore(dsn=DSN),
    import_paths=["procrastinate_demo.tasks"],
    schedule=[
        {"job": "procrastinate_demo.tasks.random_fail", "cron": {"minute": "*"}},
        {
            "job": "procrastinate_demo.tasks.sum",
            "kwargs": {"a": 1, "b": 2},
            "cron": {"second": "*/3"},
        },
        {
            "job": "procrastinate_demo.tasks.sleep",
            "kwargs": {"i": 3},
            "cron": {"second": "*/5"},
        },
    ],
)
