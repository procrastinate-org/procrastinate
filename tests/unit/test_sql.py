from procrastinate import sql


def test_parse_query_file():
    assert (
        sql.parse_query_file(
            """
-- Hello: This is ignored.
yay

-- query1 --
Select bla

-- query2 --
-- Description

SELECT blu

-- query3 --
-- multi-line
-- description
INSERT INTO blou VALUES(%(yay)s)
    """
        )
        == {
            "query1": "Select bla",
            "query2": "SELECT blu",
            "query3": "INSERT INTO blou VALUES(%(yay)s)",
        }
    )


def test_get_queries():
    assert {"defer_job", "fetch_job", "finish_job"} <= set(sql.get_queries())
