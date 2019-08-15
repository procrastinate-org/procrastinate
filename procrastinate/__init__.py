from procrastinate import metadata as _metadata_module
from procrastinate.app import App
from procrastinate.postgres import PostgresJobStore
from procrastinate.retry import BaseRetryStrategy, RetryStrategy
from procrastinate.store import BaseJobStore

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
