import cabbage

app = cabbage.App(
    job_store={
        "name": "postgres_sync",
        "dsn": "postgresql://postgres@localhost/cabbage",
    },
    import_paths=["cabbage_demo.tasks"],
)
