import pytest

from procrastinate import blueprints, exceptions, retry


def test_app_task_explicit(app, mocker):
    bp = blueprints.Blueprint()

    @bp.task(
        name="foobar",
        queue="bar",
        lock="sher",
        queueing_lock="baz",
        retry=True,
        pass_context=True,
    )
    def wrapped():
        return "foo"

    app.add_tasks_from(bp, namespace="ns")

    assert wrapped() == "foo"
    assert app.tasks["ns:foobar"].name == "ns:foobar"
    assert app.tasks["ns:foobar"].queue == "bar"
    assert app.tasks["ns:foobar"].lock == "sher"
    assert app.tasks["ns:foobar"].queueing_lock == "baz"
    assert isinstance(app.tasks["ns:foobar"].retry_strategy, retry.RetryStrategy)
    assert app.tasks["ns:foobar"].pass_context is True
    assert app.tasks["ns:foobar"] is wrapped
    assert app.tasks["ns:foobar"].func is wrapped.__wrapped__


def test_app_task_implicit(app):
    bp = blueprints.Blueprint()

    @bp.task
    def wrapped():
        return "foo"

    app.add_tasks_from(bp, namespace="ns")

    registered_task = app.tasks["ns:tests.unit.test_blueprints.wrapped"]

    assert "foo" == wrapped()
    assert "ns:tests.unit.test_blueprints.wrapped" == registered_task.name
    assert "default" == registered_task.queue
    assert registered_task is wrapped
    assert registered_task.func is wrapped.__wrapped__


def test_app_task_configure_before_binding_not_allowed(app):
    bp = blueprints.Blueprint()

    @bp.task()
    def wrapped():
        return "foo"

    with pytest.raises(exceptions.UnboundTaskError):
        wrapped.configure()
