import inspect

from procrastinate import App, Blueprint
from procrastinate.protocols import TaskCreator


# def test_task_signatures(app, mocker):
def test_task_signatures():
    """Tasks can be created in two ways, both of which need to maintain an
    identical API.  This test simple test that App.task and Blueprint.task have
    the same function signature.

    This is further enforced with protocols.TaskCreator and mypy checks.
    """

    # Check that both App.task and Blueprint.task implement Taskcreator.task
    assert inspect.signature(App.task) == inspect.signature(TaskCreator.task)
    assert inspect.signature(Blueprint.task) == inspect.signature(TaskCreator.task)
    # Sanity check
    assert inspect.signature(App.task) == inspect.signature(Blueprint.task)
