from procrastinate import metadata as _metadata_module
from procrastinate.aiopg_connector import PostgresConnector
from procrastinate.app import App
from procrastinate.job_context import JobContext
from procrastinate.retry import BaseRetryStrategy, RetryStrategy

__all__ = [
    "App",
    "JobContext",
    "BaseRetryStrategy",
    "PostgresConnector",
    "RetryStrategy",
]


_metadata = _metadata_module.extract_metadata()
__author__ = _metadata["author"]
__author_email__ = _metadata["email"]
__license__ = _metadata["license"]
__url__ = _metadata["url"]
__version__ = _metadata["version"]
