from __future__ import annotations

import pathlib
import sys
from typing import TYPE_CHECKING, cast

from typing_extensions import LiteralString

if TYPE_CHECKING:
    import importlib_resources
else:
    # https://github.com/pypa/twine/pull/551
    if sys.version_info[:2] < (3, 9):  # coverage: exclude
        import importlib_resources
    else:  # coverage: exclude
        import importlib.resources as importlib_resources

from procrastinate import connector as connector_module

migrations_path = pathlib.Path(__file__).parent / "sql" / "migrations"


class SchemaManager:
    def __init__(self, connector: connector_module.BaseConnector):
        self.connector = connector

    @staticmethod
    def get_schema() -> LiteralString:
        # procrastinate takes full responsibility for the queries, we
        # can safely vouch for them being as safe as if they were
        # defined in the code itself.
        schema_sql = (
            importlib_resources.files("procrastinate.sql") / "schema.sql"
        ).read_text(encoding="utf-8")
        return cast(LiteralString, schema_sql)

    @staticmethod
    def get_migrations_path() -> str:
        return str(migrations_path)

    def apply_schema(self) -> None:
        queries = self.get_schema()
        queries = queries.replace("%", "%%")
        self.connector.execute_query(query=queries)

    async def apply_schema_async(self) -> None:
        queries = self.get_schema()
        queries = queries.replace("%", "%%")
        await self.connector.execute_query_async(query=queries)
