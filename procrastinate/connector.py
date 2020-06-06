import asyncio
from typing import Any, Callable, Dict, Iterable, List, Optional

from procrastinate import utils

QUEUEING_LOCK_CONSTRAINT = "procrastinate_jobs_queueing_lock_idx"


class BaseSyncConnector:
    json_dumps: Optional[Callable] = None

    def close(self) -> None:
        pass

    def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        raise NotImplementedError


@utils.add_sync_api
class BaseConnector(BaseSyncConnector):
    json_dumps: Optional[Callable] = None
    json_loads: Optional[Callable] = None

    async def close_async(self) -> None:
        pass

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

    def get_sync_connector(self) -> "BaseSyncConnector":
        return self
