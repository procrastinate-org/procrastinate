import inspect

from procrastinate import blueprints


def test_task_signatures(app, mocker):
    """Tasks can be created in two ways, both of which need to maintain an
    identical API.  This test simple test that App.task and Blueprint.task have
    the same function signature.

    This is further enforced with protocols.TaskCreator and mypy checks.
    """

    bp = blueprints.Blueprint()
    assert inspect.signature(bp.task) == inspect.signature(app.task)
