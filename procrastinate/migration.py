from importlib_resources import read_text

from procrastinate import store, exceptions


class Migrator:
    def __init__(self, job_store: store.BaseJobStore):
        if job_store.asynchronous:
            raise exceptions.ProcrastinateException(
                "Migrations cannot bu run from an asynchronous job store."
            )
        self.job_store = job_store

    def get_migration_queries(self) -> str:
        return read_text("procrastinate.sql", "structure.sql")

    def migrate(self) -> None:
        queries = self.get_migration_queries()
        self.job_store.execute_query(query=queries)
