from procrastinate.contrib.django import utils


def test_connector_params():
    assert "database" in utils.connector_params()
