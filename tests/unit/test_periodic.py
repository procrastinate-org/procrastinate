import itertools

import pytest

from procrastinate import periodic


@pytest.fixture
def periodic_deferrer(job_manager):
    return periodic.PeriodicDeferrer(job_manager=job_manager)


@pytest.fixture
def task(app):
    @app.task
    def foo(timestamp):
        pass

    return foo


@pytest.fixture
def cron_task(periodic_deferrer, task):
    def _(cron="0 0 * * *"):
        return periodic_deferrer.register_task(task=task, cron=cron, name_suffix="")

    return _


def test_register_task(periodic_deferrer, task):
    periodic_deferrer.register_task(task=task, cron="0 0 * * *", name_suffix="")

    assert periodic_deferrer.periodic_tasks == [
        periodic.PeriodicTask(task=task, cron="0 0 * * *", name_suffix="", kwargs={})
    ]


def test_schedule_decorator(periodic_deferrer, task):
    periodic_deferrer.periodic_decorator(cron="0 0 * * *", name_suffix="")(task)

    assert periodic_deferrer.periodic_tasks == [
        periodic.PeriodicTask(task=task, cron="0 0 * * *", name_suffix="", kwargs={})
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
def test_get_next_tick(periodic_deferrer, cron_task, cron, expected):

    cron_task(cron="0 0 * * *")
    cron_task(cron=cron)

    # Making things easier, we'll compute things next to timestamp 0
    assert periodic_deferrer.get_next_tick(at=0) == expected


def test_get_previous_tasks(periodic_deferrer, cron_task, task):

    cron_task(cron="* * * * *")

    assert list(periodic_deferrer.get_previous_tasks(at=3600 * 24 - 1)) == [
        (task, "", {}, 3600 * 24 - 60)
    ]


def test_get_timestamp_late(periodic_deferrer, cron_task):
    task = cron_task(cron="* * * * *")

    end = 3600 * 24
    timestamps = periodic_deferrer.get_timestamps(
        periodic_task=task, since=end - 4 * 60 + 1, until=end - 1
    )

    assert list(timestamps) == [end - 3 * 60, end - 2 * 60, end - 60]


def test_get_timestamp_no_timestamp(periodic_deferrer, cron_task):
    task = cron_task(cron="* * * * *")

    end = 3600 * 24
    timestamps = periodic_deferrer.get_timestamps(
        periodic_task=task, since=end - 30, until=end - 1
    )

    assert list(timestamps) == []


def test_get_timestamp_no_since_within_delay(periodic_deferrer, cron_task):
    task = cron_task(cron="* * * * *")

    end = 3600 * 24
    timestamps = periodic_deferrer.get_timestamps(
        periodic_task=task, since=None, until=end - 1
    )

    assert list(timestamps) == [end - 60]


def test_get_timestamp_no_since_not_within_delay(periodic_deferrer, cron_task, caplog):
    task = cron_task(cron="0 0 * * *")
    caplog.set_level("DEBUG")

    end = 3600 * 24
    timestamps = periodic_deferrer.get_timestamps(
        periodic_task=task, since=None, until=end - 1
    )

    assert list(timestamps) == []
    assert [r.action for r in caplog.records] == ["ignore_periodic_task"]


@pytest.mark.asyncio
async def test_worker_no_task(periodic_deferrer, caplog):
    caplog.set_level("INFO")
    await periodic_deferrer.worker()

    assert [r.action for r in caplog.records] == ["periodic_deferrer_no_task"]


@pytest.mark.asyncio
async def test_worker_loop(job_manager, mocker, task):
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

    mock_deferrer = MockPeriodicDeferrer(job_manager=job_manager)
    mock_deferrer.register_task(task=task, cron="* * * * *", name_suffix="")
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
async def test_wait_next_tick(periodic_deferrer, mocker):
    async def wait(val):
        assert val == 5 + periodic.MARGIN

    mocker.patch("asyncio.sleep", wait)

    await periodic_deferrer.wait(5)


@pytest.mark.asyncio
async def test_defer_jobs(periodic_deferrer, task, connector, caplog):
    caplog.set_level("DEBUG")
    await periodic_deferrer.defer_jobs([(task, "", {}, 1)])

    assert connector.queries == [
        (
            "defer_periodic_job",
            {
                "queue": "default",
                "args": {"timestamp": 1},
                "defer_timestamp": 1,
                "lock": None,
                "queueing_lock": None,
                "task_name": task.name,
                "name_suffix": "",
            },
        )
    ]
    assert [r.action for r in caplog.records] == ["periodic_task_deferred"]


@pytest.mark.asyncio
async def test_defer_jobs_different_name_suffix(
    periodic_deferrer, task, connector, caplog
):
    caplog.set_level("DEBUG")
    connector.periodic_defers[(task.name, "foo")] = 1

    await periodic_deferrer.defer_jobs([(task, "bar", {}, 1)])

    assert connector.queries == [
        (
            "defer_periodic_job",
            {
                "queue": "default",
                "args": {"timestamp": 1},
                "defer_timestamp": 1,
                "lock": None,
                "queueing_lock": None,
                "task_name": task.name,
                "name_suffix": "bar",
            },
        )
    ]
    assert [r.action for r in caplog.records] == ["periodic_task_deferred"]


@pytest.mark.asyncio
async def test_defer_jobs_already(periodic_deferrer, task, connector, caplog):
    caplog.set_level("DEBUG")
    connector.periodic_defers[(task.name, "foo")] = 1

    await periodic_deferrer.defer_jobs([(task, "foo", {}, 1)])

    assert connector.queries == [
        (
            "defer_periodic_job",
            {
                "queue": "default",
                "args": {"timestamp": 1},
                "defer_timestamp": 1,
                "lock": None,
                "queueing_lock": None,
                "task_name": task.name,
                "name_suffix": "foo",
            },
        )
    ]
    assert [r.action for r in caplog.records] == ["periodic_task_already_deferred"]


@pytest.mark.asyncio
async def test_defer_jobs_queueing_lock(periodic_deferrer, app, connector, caplog):
    caplog.set_level("DEBUG")

    @app.task(queueing_lock="sher")
    def foo(timestamp):
        pass

    caplog.clear()

    await periodic_deferrer.defer_jobs([(foo, "", {}, 1), (foo, "", {}, 2)])

    assert [r.action for r in caplog.records] == [
        "periodic_task_deferred",
        "skip_periodic_task_queueing_lock",
    ]
