from __future__ import annotations

import pytest

from procrastinate import blueprints, exceptions, periodic, retry


def test_blueprint_task_aliases(blueprint, mocker):
    @blueprint.task(name="b", aliases=["c", "d"])
    def my_task():
        pass

    assert "b" == blueprint.tasks["b"].name
    assert ["c", "d"] == blueprint.tasks["b"].aliases
    assert blueprint.tasks["b"] is my_task
    assert blueprint.tasks["c"] is my_task
    assert blueprint.tasks["d"] is my_task


def test_blueprint_task_implicit(blueprint):
    @blueprint.task
    def my_task():
        return "foo"

    registered_task = blueprint.tasks["tests.unit.test_blueprints.my_task"]

    assert "foo" == my_task()
    assert "tests.unit.test_blueprints.my_task" == registered_task.name
    assert "default" == registered_task.queue
    assert registered_task is my_task
    assert registered_task.func is my_task.__wrapped__


def test_blueprint_task_configure_before_binding_not_allowed(blueprint):
    @blueprint.task()
    def my_task():
        return "foo"

    with pytest.raises(exceptions.UnboundTaskError):
        my_task.configure()


def test_register_task(blueprint):
    @blueprint.task(name="foo")
    def my_task():
        return "foo"

    assert blueprint.tasks["foo"] is my_task


def test_add_task(blueprint):
    to = {}

    blueprint._add_task(task="fake", name="foo", to=to)
    assert to == {"foo": "fake"}


def test_add_task_clash(blueprint):
    blueprint.tasks = {"foo": "fake"}
    to = {}

    with pytest.raises(exceptions.TaskAlreadyRegistered):
        blueprint._add_task(task="fake2", name="foo", to=to)

    assert to == {}


def test_register_task_clash(blueprint):
    @blueprint.task(name="foo")
    def my_task():
        return "foo"

    with pytest.raises(exceptions.TaskAlreadyRegistered):

        @blueprint.task(name="foo")
        def my_other_task():
            return "foo"

    assert blueprint.tasks == {"foo": my_task}


def test_register_task_clash_alias(blueprint):
    @blueprint.task(name="foo")
    def my_task():
        return "foo"

    with pytest.raises(exceptions.TaskAlreadyRegistered):

        @blueprint.task(name="bar", aliases=["foo"])
        def my_other_task():
            return "foo"

    assert blueprint.tasks == {"foo": my_task}


def test_add_task_alias(blueprint):
    @blueprint.task(name="foo")
    def my_task():
        return "foo"

    blueprint.add_task_alias(task=my_task, alias="bar")

    assert blueprint.tasks == {"foo": my_task, "bar": my_task}


def test_add_tasks_from(blueprint):
    other = blueprints.Blueprint()

    @blueprint.task(name="foo")
    def my_task():
        return "foo"

    @other.task(name="bar")
    def my_other_task():
        return "bar"

    blueprint.add_tasks_from(other, namespace="ns")

    assert blueprint.tasks == {"foo": my_task, "ns:bar": my_other_task}
    assert my_other_task.name == "ns:bar"


def test_add_tasks_from__periodic(blueprint):
    other = blueprints.Blueprint()

    @blueprint.periodic(cron="0 * * * 1", periodic_id="foo")
    @blueprint.task(name="foo")
    def my_task():
        return "foo"

    @other.periodic(cron="0 * * * 1", periodic_id="foo")
    @other.task(name="bar")
    def my_other_task():
        return "bar"

    blueprint.add_tasks_from(other, namespace="ns")

    assert blueprint.periodic_registry.periodic_tasks == {
        ("foo", "foo"): periodic.PeriodicTask(
            task=my_task,
            cron="0 * * * 1",
            periodic_id="foo",
            configure_kwargs={},
        ),
        ("ns:bar", "foo"): periodic.PeriodicTask(
            task=my_other_task,
            cron="0 * * * 1",
            periodic_id="foo",
            configure_kwargs={},
        ),
    }


def test_add_tasks_from_clash(blueprint):
    other = blueprints.Blueprint()

    @blueprint.task(name="ns:foo")
    def my_task():
        return "foo"

    @other.task(name="foo")
    def my_other_task():
        return "foo"

    with pytest.raises(exceptions.TaskAlreadyRegistered):
        blueprint.add_tasks_from(other, namespace="ns")

    assert blueprint.tasks == {"ns:foo": my_task}
    assert my_other_task.name == "foo"


def test_add_tasks_from_clash_alias(blueprint):
    other = blueprints.Blueprint()

    @blueprint.task(name="foo", aliases=["ns:foo"])
    def my_task():
        return "foo"

    @other.task(name="foo")
    def my_other_task():
        return "foo"

    with pytest.raises(exceptions.TaskAlreadyRegistered):
        blueprint.add_tasks_from(other, namespace="ns")

    assert blueprint.tasks == {"foo": my_task, "ns:foo": my_task}
    assert my_other_task.name == "foo"


def test_add_tasks_from_clash_other_alias(blueprint):
    other = blueprints.Blueprint()

    @blueprint.task(name="ns:foo")
    def my_task():
        return "foo"

    @other.task(name="bar", aliases=["foo"])
    def my_other_task():
        return "bar"

    with pytest.raises(exceptions.TaskAlreadyRegistered):
        blueprint.add_tasks_from(other, namespace="ns")

    assert blueprint.tasks == {"ns:foo": my_task}
    assert my_other_task.name == "bar"


def test_blueprint_task_explicit(blueprint, mocker):
    @blueprint.task(
        name="foobar",
        queue="bar",
        lock="sher",
        queueing_lock="baz",
        retry=True,
        pass_context=True,
        aliases=["a"],
    )
    def my_task():
        return "foo"

    assert my_task() == "foo"
    assert blueprint.tasks["foobar"].name == "foobar"
    assert blueprint.tasks["foobar"].queue == "bar"
    assert blueprint.tasks["foobar"].lock == "sher"
    assert blueprint.tasks["foobar"].queueing_lock == "baz"
    assert isinstance(blueprint.tasks["foobar"].retry_strategy, retry.RetryStrategy)
    assert blueprint.tasks["foobar"].pass_context is True
    assert blueprint.tasks["foobar"] is my_task
    assert blueprint.tasks["foobar"].func is my_task.__wrapped__
    assert blueprint.tasks["a"] is blueprint.tasks["foobar"]


def test_app_periodic(blueprint):
    @blueprint.periodic(cron="0 * * * 1", periodic_id="foo")
    @blueprint.task
    def yay(timestamp):
        pass

    assert len(blueprint.periodic_registry.periodic_tasks) == 1
    assert blueprint.periodic_registry.periodic_tasks[yay.name, "foo"].task == yay
