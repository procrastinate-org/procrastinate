from procrastinate import metadata as _metadata_module
from procrastinate.aiopg_connector import PostgresConnector, PostgresJobStore
from procrastinate.app import App
from procrastinate.retry import BaseRetryStrategy, RetryStrategy

__all__ = [
    "App",
    "BaseRetryStrategy",
    "PostgresConnector",
    "PostgresJobStore",
    "RetryStrategy",
]


_metadata = _metadata_module.extract_metadata()
__author__ = _metadata["author"]
__author_email__ = _metadata["email"]
__license__ = _metadata["license"]
__url__ = _metadata["url"]
__version__ = _metadata["version"]
