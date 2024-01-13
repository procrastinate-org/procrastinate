from __future__ import annotations

import importlib.metadata as importlib_metadata
from typing import Mapping


def extract_metadata() -> Mapping[str, str]:
    metadata = importlib_metadata.metadata("procrastinate")

    return {
        "author": metadata["Author"],
        "email": metadata["Author-email"],
        "license": metadata["License"],
        "url": metadata["Home-page"],
        "version": metadata["Version"],
    }
