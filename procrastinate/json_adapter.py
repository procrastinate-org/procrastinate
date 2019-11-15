import json
from datetime import date, datetime

import psycopg2


class JsonAdapter(psycopg2.extras.Json):
    """
    Convert a given dict to JSON, while handling conversion of some
    otherwise non JSON serialisable objects.
    """

    def encoder(self, obj) -> str:
        if isinstance(obj, (date, datetime)):
            # returns the date or datetime in ISO format
            return str(obj)

        raise TypeError(f"Object of type '{type(obj)}' is not JSON serializable")

    def dumps(self, obj) -> str:
        return json.dumps(obj, default=self.encoder)
