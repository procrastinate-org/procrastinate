import pytest

import procrastinate


def test_app_deprecation(caplog, mocker):
    connector = mocker.patch(
        "procrastinate.aiopg_connector.PostgresConnector.create_with_pool"
    )
    with pytest.deprecated_call():
        procrastinate.PostgresJobStore()
    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[0].message.startswith("Deprecation Warning")
    connector.assert_called()
