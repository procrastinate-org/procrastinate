import pytest

import procrastinate


def test_app_deprecation(caplog):
    with pytest.deprecated_call():
        procrastinate.PostgresJobStore()
    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[0].message.startswith("Deprecation Warning")
