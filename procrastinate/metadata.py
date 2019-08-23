from typing import Mapping

import importlib_metadata


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
