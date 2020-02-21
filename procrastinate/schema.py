import pathlib
import re

import pkg_resources
from importlib_resources import read_text

from procrastinate import connector as connector_module
from procrastinate import sql, utils

migrations_dir = pathlib.Path(__file__).parent / "sql" / "migrations"
migration_script_pattern = re.compile(r"^delta_(\d+\.\d+\.\d+)_*\w*\.sql")


@utils.add_sync_api
class SchemaManager:
    def __init__(self, connector: connector_module.BaseConnector):

        self.connector = connector

    @staticmethod
    def get_schema() -> str:
        return read_text("procrastinate.sql", "schema.sql")

    @staticmethod
    def get_version():
        version_ = pkg_resources.parse_version("1.0.0")
        for script in migrations_dir.glob("*.sql"):
            m = migration_script_pattern.match(script.name)
            if m:
                v = pkg_resources.parse_version(m.group(1))
                if v > version_:
                    version_ = v
        return str(version_)

    async def apply_schema_async(self) -> None:
        queries = self.get_schema()
        await self.connector.execute_query(query=queries)
        await self.connector.execute_query(
            query=sql.queries["set_schema_version"], version=self.get_version(),
        )
