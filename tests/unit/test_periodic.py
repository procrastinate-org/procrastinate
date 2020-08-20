import itertools

import pytest

from procrastinate import periodic


@pytest.fixture
def deferrer(job_store):
    return periodic.PeriodicDeferrer(job_store=job_store)


@pytest.fixture
def task(app):
    @app.task
    def foo(timestamp):
        pass

    return foo


@pytest.fixture
def cron_task(deferrer, task):
    def _(cron="0 0 * * *"):
        return deferrer.register_task(task=task, cron=cron)

    return _


def test_register_task(deferrer, task):
    deferrer.register_task(task=task, cron="0 0 * * *")

    assert deferrer.periodic_tasks == [
        periodic.PeriodicTask(task=task, cron="0 0 * * *")
    ]


def test_schedule_decorator(deferrer, task):
    deferrer.periodic_decorator(cron="0 0 * * *")(task)

    assert deferrer.periodic_tasks == [
        periodic.PeriodicTask(task=task, cron="0 0 * * *")
    ]


@pytest.mark.parametrize(
    "cron, expected",
    [
        ("0 0 0 * *", 3600 * 24),
        ("0 0 * * *", 3600 * 24),
        ("0 * * * *", 3600),
        ("* * * * *", 60),
        ("* * * * * */5", 5),
    ],
)
def test_get_next_tick(deferrer, cron_task, cron, expected):

    cron_task(cron="0 0 * * *")
    cron_task(cron=cron)

    # Making things easier, we'll compute things next to timestamp 0
    assert deferrer.get_next_tick(at=0) == expected


def test_get_previous_tasks(deferrer, cron_task, task):

    cron_task(cron="* * * * *")

    assert list(deferrer.get_previous_tasks(at=3600 * 24 - 1)) == [
        (task, 3600 * 24 - 60)
    ]


def test_get_previous_tasks_known_schedule(deferrer, cron_task, task):

    cron_task(cron="* * * * *")

    deferrer.last_defers[task.name] = 3600 * 24 - 60

    assert list(deferrer.get_previous_tasks(at=3600 * 24 - 1)) == []


def test_get_previous_tasks_too_old(deferrer, cron_task, task, caplog):

    cron_task(cron="0 0 0 * *")
    caplog.set_level("DEBUG")

    assert list(deferrer.get_previous_tasks(at=3600 * 24 - 1)) == []

    assert [r.action for r in caplog.records] == ["ignore_periodic_task"]


@pytest.mark.asyncio
async def test_worker_no_task(deferrer, caplog):
    caplog.set_level("INFO")
    await deferrer.worker()

    assert [r.action for r in caplog.records] == ["periodic_deferrer_no_task"]


@pytest.mark.asyncio
async def test_worker_loop(job_store, mocker, task):
    # The idea of this test is to make the inifite loop raise at some point
    mock = mocker.Mock()
    mock.wait_next_tick.side_effect = [None, None, ValueError]
    counter = itertools.count()

    class MockPeriodicDeferrer(periodic.PeriodicDeferrer):
        async def defer_jobs(self, jobs_to_defer):
            mock.defer_jobs()

        async def wait(self, next_tick):
            mock.wait_next_tick(next_tick)

        def get_next_tick(self, at):
            return next(counter)

    mock_deferrer = MockPeriodicDeferrer(job_store=job_store)
    mock_deferrer.register_task(task=task, cron="* * * * *")
    with pytest.raises(ValueError):
        await mock_deferrer.worker()

    assert mock.mock_calls == [
        mocker.call.defer_jobs(),
        mocker.call.wait_next_tick(0),
        mocker.call.defer_jobs(),
        mocker.call.wait_next_tick(1),
        mocker.call.defer_jobs(),
        mocker.call.wait_next_tick(2),
    ]


@pytest.mark.asyncio
async def test_wait_next_tick(deferrer, mocker):
    async def wait(val):
        assert val == 5 + periodic.MARGIN

    mocker.patch("asyncio.sleep", wait)

    await deferrer.wait(5)


@pytest.mark.asyncio
async def test_defer_jobs(deferrer, task, connector, caplog):
    caplog.set_level("DEBUG")
    await deferrer.defer_jobs([(task, 1)])

    assert connector.queries == [
        (
            "defer_periodic_job",
            {
                "queue": "default",
                "defer_timestamp": 1,
                "task_name": "tests.unit.test_periodic.foo",
            },
        )
    ]
    assert [r.action for r in caplog.records] == ["periodic_task_deferred"]


@pytest.mark.asyncio
async def test_defer_jobs_already(deferrer, task, connector, caplog):
    caplog.set_level("DEBUG")
    connector.periodic_defers[task.name] = 1

    await deferrer.defer_jobs([(task, 1)])

    assert connector.queries == [
        (
            "defer_periodic_job",
            {
                "queue": "default",
                "defer_timestamp": 1,
                "task_name": "tests.unit.test_periodic.foo",
            },
        )
    ]
    assert [r.action for r in caplog.records] == ["periodic_task_already_deferred"]
