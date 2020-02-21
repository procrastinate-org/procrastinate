import pathlib
import re

import pkg_resources
from importlib_resources import read_text

from procrastinate import connector as connector_module
from procrastinate import utils

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
        matches = (
            migration_script_pattern.match(script.name)
            for script in migrations_dir.glob("*.sql")
        )
        versions = (match.group(1) for match in matches if match)
        return str(max(versions, key=pkg_resources.parse_version))

    async def apply_schema_async(self) -> None:
        queries = self.get_schema()
        await self.connector.execute_query(query=queries)
