import itertools

import pytest

from procrastinate import scheduler as scheduler_module


@pytest.fixture
def scheduler(job_store):
    return scheduler_module.Scheduler(job_store=job_store)


@pytest.fixture
def task(app):
    @app.task
    def foo(timestamp):
        pass

    return foo


@pytest.fixture
def cron_task(scheduler, task):
    def _(cron="0 0 * * *"):
        return scheduler.register_task(task=task, cron=cron)

    return _


def test_register_task(scheduler, task):
    scheduler.register_task(task=task, cron="0 0 * * *")

    assert scheduler.periodic_tasks == [
        scheduler_module.PeriodicTask(task=task, cron="0 0 * * *")
    ]


def test_schedule_decorator(scheduler, task):
    scheduler.schedule_decorator(cron="0 0 * * *")(task)

    assert scheduler.periodic_tasks == [
        scheduler_module.PeriodicTask(task=task, cron="0 0 * * *")
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
def test_get_next_tick(scheduler, cron_task, cron, expected):

    cron_task(cron="0 0 * * *")
    cron_task(cron=cron)

    # Making things easier, we'll compute things next to timestamp 0
    assert scheduler.get_next_tick(now=0) == expected


def test_get_previous_tasks(scheduler, cron_task, task):

    cron_task(cron="* * * * *")

    assert list(scheduler.get_previous_tasks(now=3600 * 24 - 1)) == [
        (task, 3600 * 24 - 60)
    ]


def test_get_previous_tasks_known_schedule(scheduler, cron_task, task):

    cron_task(cron="* * * * *")

    scheduler.last_schedules_for_task[task.name] = 3600 * 24 - 60

    assert list(scheduler.get_previous_tasks(now=3600 * 24 - 1)) == []


def test_get_previous_tasks_too_old(scheduler, cron_task, task, caplog):

    cron_task(cron="0 0 0 * *")
    caplog.set_level("DEBUG")

    assert list(scheduler.get_previous_tasks(now=3600 * 24 - 1)) == []

    assert [r.action for r in caplog.records] == ["ignore_periodic_task"]


@pytest.mark.asyncio
async def test_worker_no_task(scheduler, caplog):
    caplog.set_level("INFO")
    await scheduler.worker()

    assert [r.action for r in caplog.records] == ["scheduler_no_task"]


@pytest.mark.asyncio
async def test_worker_loop(job_store, mocker, task):
    # The idea of this test is to make the inifite loop raise at some point
    mock = mocker.Mock()
    mock.wait_next_tick.side_effect = [None, None, ValueError]
    counter = itertools.count()

    class MockScheduler(scheduler_module.Scheduler):
        async def defer_jobs(self, jobs_to_defer):
            mock.defer_jobs()

        async def wait(self, next_tick):
            mock.wait_next_tick(next_tick)

        def get_next_tick(self):
            return next(counter)

    mock_scheduler = MockScheduler(job_store=job_store)
    mock_scheduler.register_task(task=task, cron="* * * * *")
    with pytest.raises(ValueError):
        await mock_scheduler.worker()

    assert mock.mock_calls == [
        mocker.call.defer_jobs(),
        mocker.call.wait_next_tick(0),
        mocker.call.defer_jobs(),
        mocker.call.wait_next_tick(1),
        mocker.call.defer_jobs(),
        mocker.call.wait_next_tick(2),
    ]


@pytest.mark.asyncio
async def test_wait_next_tick(scheduler, mocker):
    async def wait(val):
        assert val == 5 + scheduler_module.MARGIN

    mocker.patch("asyncio.sleep", wait)

    await scheduler.wait(5)


@pytest.mark.asyncio
async def test_defer_jobs(scheduler, task, connector, caplog):
    caplog.set_level("DEBUG")
    await scheduler.defer_jobs([(task, 1)])

    assert connector.queries == [
        (
            "defer_periodic_job",
            {
                "queue": "default",
                "schedule_timestamp": 1,
                "task_name": "tests.unit.test_scheduler.foo",
            },
        )
    ]
    assert [r.action for r in caplog.records] == ["periodic_task_deferred"]


@pytest.mark.asyncio
async def test_defer_jobs_already(scheduler, task, connector, caplog):
    caplog.set_level("DEBUG")
    connector.schedules[task.name] = 1

    await scheduler.defer_jobs([(task, 1)])

    assert connector.queries == [
        (
            "defer_periodic_job",
            {
                "queue": "default",
                "schedule_timestamp": 1,
                "task_name": "tests.unit.test_scheduler.foo",
            },
        )
    ]
    assert [r.action for r in caplog.records] == ["periodic_task_already_deferred"]
