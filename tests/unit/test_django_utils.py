import pathlib

from procrastinate.contrib.django import utils


def test_get_sql():
    migration_name = "baseline-0.5.0.sql"

    migration_path = (
        (pathlib.Path(__file__).parent.parent.parent)
        / "procrastinate"
        / "sql"
        / "migrations"
    )
    with open(migration_path / migration_name, "rb") as f:
        expected = f.read().decode()

    assert utils.get_sql(migration_name) == expected
