from importlib_resources import read_text

from procrastinate import store


class Migrator:
    def __init__(self, job_store: store.BaseJobStore):
        self.job_store = job_store

    def get_migration_queries(self) -> str:
        return read_text("procrastinate", "structure.sql")

    def migrate(self) -> None:
        queries = self.get_migration_queries()
        self.job_store.execute_queries(queries=queries)
