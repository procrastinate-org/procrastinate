import cabbage

app = cabbage.App(
    job_store=cabbage.PostgresJobStore("postgresql://postgres@localhost/cabbage"),
    import_paths=["cabbage_demo.tasks"],
)
