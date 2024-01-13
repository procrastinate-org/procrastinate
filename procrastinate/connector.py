import asyncio
from typing import Any, Callable, Dict, Iterable, List, Optional

from procrastinate import exceptions, utils

Pool = Any
Engine = Any


class BaseConnector:
    json_dumps: Optional[Callable] = None
    json_loads: Optional[Callable] = None

    def get_sync_connector(self) -> "BaseConnector":
        raise NotImplementedError

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

    def execute_query(self, query: str, **arguments: Any) -> None:
        return utils.async_to_sync(self.execute_query_async, query, **arguments)

    def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        return utils.async_to_sync(self.execute_query_one_async, query, **arguments)

    def execute_query_all(self, query: str, **arguments: Any) -> List[Dict[str, Any]]:
        return utils.async_to_sync(self.execute_query_all_async, query, **arguments)

    async def listen_notify(
        self, event: asyncio.Event, channels: Iterable[str]
    ) -> None:
        raise NotImplementedError
