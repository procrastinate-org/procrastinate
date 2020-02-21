from typing import Any, Callable, Dict, List, Optional

SOCKET_TIMEOUT = 5.0  # seconds


class BaseConnector:
    json_dumps: Optional[Callable] = None
    json_loads: Optional[Callable] = None

    async def close(self) -> None:
        pass

    async def execute_query(self, query: str, **arguments: Any) -> None:
        raise NotImplementedError

    async def execute_query_one(self, query: str, **arguments: Any) -> Dict[str, Any]:
        raise NotImplementedError

    async def execute_query_all(
        self, query: str, **arguments: Any
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def make_dynamic_query(self, query: str, **identifiers: str) -> str:
        raise NotImplementedError
