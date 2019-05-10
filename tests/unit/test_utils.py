import pytest

from cabbage import utils


def test_load_from_path():
    loads = utils.load_from_path("json.loads")
    import json

    assert loads is json.loads


@pytest.mark.parametrize("input", ["foobarbaz", "fooobarbaz.loads", "json.foobarbaz"])
def test_load_from_path_error(input):
    with pytest.raises(ImportError):
        utils.load_from_path(input)
