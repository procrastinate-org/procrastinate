import pytest
import psycopg2


@pytest.fixture(scope="session")
def setup_db():

    connection = psycopg2.connect("")

    with connection.cursor() as cursor:
        cursor.execute("DROP DATABASE IF EXISTS %s", ("cabbage_test_template",))
        cursor.execute("CREATE DATABASE %s", ("cabbage_test_template",))
        with open("migrations.sql") as migrations:
            cursor.execute(migrations.read())

    connection.commit()
    return connection


@pytest.fixture
def db(setup_db):
    with setup_db.cursor() as cursor:
        cursor.execute("DROP DATABASE IF EXISTS %s", ("cabbage_test",))
        cursor.execute(
            "CREATE DATABASE %s TEMPLATE ", ("cabbage_test", "cabbage_test_template")
        )
    # Delete "cabbage_test" if exists
    # Create "cabbage_test" from "cabbage_test_template"
    pass
