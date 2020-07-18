import pathlib

from django.db import connection


def test_django_migrations_run_properly(db):
    # At this point, with the db fixture, we have all migrations applied
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM procrastinate_jobs")


def test_no_missing_migration():
    procrastinate_dir = pathlib.Path(__file__).parent.parent.parent / "procrastinate"
    django_migrations_path = procrastinate_dir / "contrib" / "django" / "migrations"
    django_migrations = [
        e for e in list(django_migrations_path.iterdir()) if e.name.startswith("0")
    ]
    sql_migrations_path = procrastinate_dir / "sql" / "migrations"
    sql_migrations = list(sql_migrations_path.iterdir())

    assert len(sql_migrations) > 0
    assert len(django_migrations) > 0

    assert len(sql_migrations) == len(
        django_migrations
    ), "Some django migrations are missing"
