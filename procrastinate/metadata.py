import sys
from typing import Mapping

# https://github.com/pypa/twine/pull/551
if sys.version_info[:2] < (3, 8):  # coverage: exclude
    import importlib_metadata
else:  # coverage: exclude
    import importlib.metadata as importlib_metadata


def extract_metadata() -> Mapping[str, str]:

    # Backport of Python 3.8's future importlib.metadata()
    metadata = importlib_metadata.metadata("procrastinate")

    return {
        "author": metadata["Author"],
        "email": metadata["Author-email"],
        "license": metadata["License"],
        "url": metadata["Home-page"],
        "version": metadata["Version"],
    }
