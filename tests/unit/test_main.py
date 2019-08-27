import pytest

from procrastinate import __main__


@pytest.mark.parametrize("name, called", [("something", False), ("__main__", True)])
def test_main(mocker, name, called):
    cli = mocker.patch("procrastinate.cli.cli")
    __main__.main(name)
    assert cli.called is called
