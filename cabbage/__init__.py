from cabbage import metadata as _metadata_module
from cabbage.app import App
from cabbage.postgres import PostgresJobStore
from cabbage.retry import BaseRetryStrategy, RetryStrategy
from cabbage.store import BaseJobStore

__all__ = [
    "App",
    "BaseJobStore",
    "BaseRetryStrategy",
    "PostgresJobStore",
    "RetryStrategy",
]


_metadata = _metadata_module.extract_metadata()
__author__ = _metadata["author"]
__author_email__ = _metadata["email"]
__copyright__ = _metadata["copyright"]
__url__ = _metadata["url"]
__version__ = _metadata["version"]
