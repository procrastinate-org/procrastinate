from cabbage import metadata as _metadata_module
from cabbage.app import App
from cabbage.postgres import PostgresJobStore
from cabbage.retry import BaseRetryStrategy, RetryStrategy

__all__ = ["App", "PostgresJobStore", "RetryStrategy", "BaseRetryStrategy"]


_metadata = _metadata_module.extract_metadata()
__author__ = _metadata["author"]
__author_email__ = _metadata["email"]
__copyright__ = _metadata["copyright"]
__url__ = _metadata["url"]
__version__ = _metadata["version"]
