from procrastinate import metadata as _metadata_module
from procrastinate.aiopg_connector import AiopgConnector
from procrastinate.app import App
from procrastinate.blueprints import Blueprint
from procrastinate.connector import BaseConnector
from procrastinate.job_context import JobContext
from procrastinate.psycopg2_connector import Psycopg2Connector
from procrastinate.retry import BaseRetryStrategy, RetryStrategy

__all__ = [
    "App",
    "Blueprint",
    "JobContext",
    "BaseConnector",
    "BaseRetryStrategy",
    "AiopgConnector",
    "Psycopg2Connector",
    "RetryStrategy",
]


_metadata = _metadata_module.extract_metadata()
__author__ = _metadata["author"]
__author_email__ = _metadata["email"]
__license__ = _metadata["license"]
__url__ = _metadata["url"]
__version__ = _metadata["version"]
