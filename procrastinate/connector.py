import asyncio
from typing import Any, Callable, Dict, Iterable, List, Optional

from procrastinate import exceptions, utils

QUEUEING_LOCK_CONSTRAINT = "procrastinate_jobs_queueing_lock_idx"


Pool = Any  # The connection pool can be any pool object compatible with the database.


class BaseConnector:
    json_dumps: Optional[Callable] = None
    json_loads: Optional[Callable] = None

    def open(self, pool: Optional[Pool] = None) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError

    def execute_query(self, query: str, **arguments: Any) -> None:
        raise NotImplementedError

    def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        raise NotImplementedError

    def execute_query_all(self, query: str, **arguments: Any) -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def open_async(self, pool: Optional[Pool] = None) -> None:
        raise exceptions.SyncConnectorConfigurationError

    async def close_async(self) -> None:
        raise exceptions.SyncConnectorConfigurationError

    async def execute_query_async(self, query: str, **arguments: Any) -> None:
        raise exceptions.SyncConnectorConfigurationError

    async def execute_query_one_async(
        self, query: str, **arguments: Any
    ) -> Dict[str, Any]:
        raise exceptions.SyncConnectorConfigurationError

    async def execute_query_all_async(
        self, query: str, **arguments: Any
    ) -> List[Dict[str, Any]]:
        raise exceptions.SyncConnectorConfigurationError

    async def listen_notify(
        self, event: asyncio.Event, channels: Iterable[str]
    ) -> None:
        raise exceptions.SyncConnectorConfigurationError

    def __del__(self):
        self.close()


@utils.add_sync_api
class BaseAsyncConnector(BaseConnector):
    async def open_async(self, pool: Optional[Pool] = None) -> None:
        raise NotImplementedError

    async def close_async(self) -> None:
        raise NotImplementedError

    async def execute_query_async(self, query: str, **arguments: Any) -> None:
        raise NotImplementedError

    async def execute_query_one_async(
        self, query: str, **arguments: Any
    ) -> Dict[str, Any]:
        raise NotImplementedError

    async def execute_query_all_async(
        self, query: str, **arguments: Any
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def listen_notify(
        self, event: asyncio.Event, channels: Iterable[str]
    ) -> None:
        raise NotImplementedError
