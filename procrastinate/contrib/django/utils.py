import pathlib


def get_sql(name: str) -> str:
    sql_path = (pathlib.Path(__file__).parent.parent.parent) / "sql" / "migrations"
    with open(sql_path / name, "rb") as f:
        return f.read().decode()
