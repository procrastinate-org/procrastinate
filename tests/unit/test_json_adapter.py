from psycopg2._json import Json

from procrastinate.json_adapter import JsonAdapter


def test_default_json_adapter():
    d = {
        "lorem": "ipsum",
        "int": 5,
        "float": 5.5
    }

    json_default = str(Json(d))
    json_adapter = str(JsonAdapter(d))

    assert json_adapter == json_default
