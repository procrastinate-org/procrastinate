import re
from typing import Dict

from importlib_resources import read_text

QUERIES_REGEX = re.compile(r"(?:\n|^)-- ([a-z0-9_]+) --\n(?:-- .+\n)*", re.MULTILINE)


def parse_query_file(query_file: str) -> Dict["str", "str"]:
    split = iter(QUERIES_REGEX.split(query_file))
    next(split)  # Consume the header of the file
    result = {}
    try:
        while True:
            key = next(split)
            value = next(split).strip()
            result[key] = value
    except StopIteration:
        pass
    return result


def get_queries() -> Dict["str", "str"]:
    return parse_query_file(read_text("procrastinate.sql", "queries.sql"))


queries = get_queries()
