import cabbage

app = cabbage.App(
    postgres_dsn="postgresql://postgres@localhost/cabbage",
    import_paths=["cabbage_demo.tasks"],
)
