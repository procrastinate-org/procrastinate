import asyncio
import logging

import pytest

from procrastinate import exceptions, job_context, jobs, tasks, worker

from .. import conftest

pytestmark = pytest.mark.asyncio


@pytest.fixture
def test_worker(app):
    return worker.Worker(app, queues=None)


@pytest.fixture
def context(app):
    def _(job):
        return job_context.JobContext(app=app, worker_name="worker", job=job)

    return _


async def test_run(test_worker, mocker, caplog):
    caplog.set_level("INFO")

    single_worker = mocker.Mock()

    async def mock(worker_id):
        single_worker(worker_id=worker_id)

    test_worker.single_worker = mock

    await test_worker.run()

    single_worker.assert_called()

    assert set(caplog.messages) == {
        "Starting worker on all queues",
        "Stopped worker on all queues",
        "No periodic task found, periodic deferrer will not run.",
    }


@pytest.mark.parametrize(
    "side_effect, status",
    [
        (None, "succeeded"),
        (exceptions.JobError(), "failed"),
        (exceptions.TaskNotFound(), "failed"),
    ],
)
async def test_process_job(
    mocker, test_worker, job_factory, connector, side_effect, status
):
    async def coro(*args, **kwargs):
        pass

    test_worker.run_job = mocker.Mock(side_effect=side_effect or coro)
    job = job_factory(id=1)
    await test_worker.job_store.defer_job_async(job)

    await test_worker.process_job(job=job)

    test_worker.run_job.assert_called_with(
        job=job, worker_id=0,
    )
    assert connector.jobs[1]["status"] == status


async def test_process_job_retry_failed_job(
    mocker, test_worker, job_factory, connector
):
    async def coro(*args, **kwargs):
        pass

    scheduled_at = conftest.aware_datetime(2000, 1, 1)
    test_worker.run_job = mocker.Mock(
        side_effect=exceptions.JobRetry(scheduled_at=scheduled_at)
    )
    job = job_factory(id=1)
    await test_worker.job_store.defer_job_async(job)

    await test_worker.process_job(job=job, worker_id=0)

    test_worker.run_job.assert_called_with(job=job, worker_id=0)
    assert connector.jobs[1]["status"] == "todo"
    assert connector.jobs[1]["scheduled_at"] == scheduled_at


async def test_run_job(app):
    result = []

    @app.task(queue="yay", name="task_func")
    def task_func(a, b):
        result.append(a + b)

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        queueing_lock="houba",
        task_name="task_func",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    await test_worker.run_job(job=job, worker_id=3)

    assert result == [12]


async def test_run_job_async(app):
    result = []

    @app.task(queue="yay", name="task_func")
    async def task_func(a, b):
        result.append(a + b)

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        queueing_lock="houba",
        task_name="task_func",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    await test_worker.run_job(job=job, worker_id=3)

    assert result == [12]


async def test_run_job_log_result(caplog, app):
    caplog.set_level("INFO")

    result = []

    def task_func(a, b):  # pylint: disable=unused-argument
        s = a + b
        result.append(s)
        return s

    task = tasks.Task(task_func, app=app, queue="yay", name="job")

    app.tasks = {"task_func": task}

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        queueing_lock="houba",
        task_name="task_func",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    await test_worker.run_job(job=job, worker_id=3)

    assert result == [12]

    records = [record for record in caplog.records if record.action == "job_success"]
    assert len(records) == 1
    record = records[0]
    assert record.result == 12
    assert "Result: 12" in record.message


@pytest.mark.parametrize(
    "worker_name, logger_name, record_worker_name",
    [(None, "worker", "worker"), ("w1", "worker.w1", "w1")],
)
async def test_run_job_log_name(
    caplog, app, worker_name, logger_name, record_worker_name
):
    caplog.set_level("INFO")

    test_worker = worker.Worker(app, name=worker_name, wait=False)

    @app.task
    def task():
        pass

    await task.defer_async()

    await test_worker.run()

    # We're not interested in defer logs
    records = [r for r in caplog.records if "worker" in r.name]

    assert len(records)
    record_names = [record.name for record in records]
    assert all([name.endswith(logger_name) for name in record_names])

    worker_names = [getattr(record, "worker", {}).get("name") for record in records]
    assert all([name == record_worker_name for name in worker_names])


async def test_run_job_error(app):
    def job(a, b):  # pylint: disable=unused-argument
        raise ValueError("nope")

    task = tasks.Task(job, app=app, queue="yay", name="job")
    task.func = job

    app.tasks = {"job": task}

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        queueing_lock="houba",
        task_name="job",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    with pytest.raises(exceptions.JobError):
        await test_worker.run_job(job=job, worker_id=3)


async def test_run_job_retry(app):
    def job(a, b):  # pylint: disable=unused-argument
        raise ValueError("nope")

    task = tasks.Task(job, app=app, queue="yay", name="job", retry=True)
    task.func = job

    app.tasks = {"job": task}

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="job",
        queueing_lock="houba",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    with pytest.raises(exceptions.JobRetry):
        await test_worker.run_job(job=job, worker_id=3)


async def test_run_job_not_found(app):
    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        queueing_lock="houba",
        task_name="job",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    with pytest.raises(exceptions.TaskNotFound):
        await test_worker.run_job(job=job, worker_id=3)


async def test_run_job_pass_context(app):
    result = []

    @app.task(queue="yay", name="job", pass_context=True)
    def task_func(test_context, a):
        result.extend([test_context, a])

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 1},
        lock="sherlock",
        queueing_lock="houba",
        task_name="job",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"], name="my_worker")
    context = job_context.JobContext(
        worker_name="my_worker",
        worker_id=3,
        worker_queues=["yay"],
        job=job,
        task=task_func,
    )
    test_worker.current_contexts[3] = context
    await test_worker.run_job(job=job, worker_id=3)

    assert result == [
        context,
        1,
    ]


async def test_run_job_concurrency_warning(app, caplog):
    # Running a sync task with concurrency > 1 should raise a warning
    result = []
    caplog.set_level(logging.WARNING)

    @app.task(queue="yay", name="job")
    def task_func(a):
        result.append(a)

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 1},
        lock="sherlock",
        queueing_lock="houba",
        task_name="job",
        queue="yay",
    )
    test_worker = worker.Worker(app, concurrency=2)
    await test_worker.run_job(job=job, worker_id=0)

    assert result == [1]
    assert [(r.action, r.levelname) for r in caplog.records] == [
        ("concurrent_sync_task", "WARNING")
    ], caplog.records


async def test_wait_for_job_with_job(app, mocker):
    test_worker = worker.Worker(app)
    # notify_event is set to None initially, and we skip run()
    test_worker.notify_event = mocker.Mock()

    wait_for = mocker.Mock()

    async def mock(coro, timeout):
        wait_for(coro, timeout=timeout)

    mocker.patch("asyncio.wait_for", mock)

    await test_worker.wait_for_job(timeout=42)

    wait_for.assert_called_with(test_worker.notify_event.wait.return_value, timeout=42)

    assert test_worker.notify_event.mock_calls == [
        mocker.call.clear(),
        mocker.call.wait(),
        mocker.call.clear(),
    ]


async def test_wait_for_job_without_job(app, mocker):
    test_worker = worker.Worker(app)
    # notify_event is set to None initially, and we skip run()
    test_worker.notify_event = mocker.Mock()

    wait_for = mocker.Mock(side_effect=asyncio.TimeoutError)

    async def mock(coro, timeout):
        wait_for(coro, timeout=timeout)

    mocker.patch("asyncio.wait_for", mock)

    await test_worker.wait_for_job(timeout=42)

    wait_for.assert_called_with(test_worker.notify_event.wait.return_value, timeout=42)

    assert test_worker.notify_event.mock_calls == [
        mocker.call.clear(),
        mocker.call.wait(),
    ]


async def test_single_worker_no_wait(app, mocker):
    process_job = mocker.Mock()
    wait_for_job = mocker.Mock()

    class TestWorker(worker.Worker):
        async def process_job(self, job):
            process_job(job=job)

        async def wait_for_job(self, timeout):
            wait_for_job(timeout)

    await TestWorker(app=app, wait=False).single_worker(worker_id=0)

    assert process_job.called is False
    assert wait_for_job.called is False


async def test_single_worker_stop_during_execution(app, mocker):
    process_job = mocker.Mock()
    wait_for_job = mocker.Mock()

    await app.configure_task("bla").defer_async()

    class TestWorker(worker.Worker):
        async def process_job(self, job, worker_id):
            process_job(job=job, worker_id=worker_id)
            self.stop_requested = True

        async def wait_for_job(self, timeout):
            wait_for_job(timeout=timeout)

    await TestWorker(app=app).single_worker(worker_id=0)

    assert wait_for_job.called is False
    process_job.assert_called_once()


async def test_single_worker_stop_during_wait(app, mocker):
    process_job = mocker.Mock()
    wait_for_job = mocker.Mock()

    await app.configure_task("bla").defer_async()

    class TestWorker(worker.Worker):
        async def process_job(self, job, worker_id):
            process_job(job=job, worker_id=worker_id)

        async def wait_for_job(self, timeout):
            wait_for_job()
            self.stop_requested = True

    await TestWorker(app=app).single_worker(worker_id=0)

    process_job.assert_called_once()
    wait_for_job.assert_called_once()


async def test_single_worker_spread_wait(app, mocker):
    process_job = mocker.Mock()
    wait_for_job = mocker.Mock()

    await app.configure_task("bla").defer_async()

    class TestWorker(worker.Worker):
        stop = False

        async def process_job(self, job, worker_id):
            process_job(job=job, worker_id=worker_id)

        async def wait_for_job(self, timeout):
            wait_for_job(timeout)
            self.stop_requested = self.stop
            self.stop = True

    await TestWorker(app=app, timeout=4, concurrency=7).single_worker(worker_id=3)

    process_job.assert_called_once()
    assert wait_for_job.call_args_list == [mocker.call(4 * (3 + 1)), mocker.call(4 * 7)]


def test_context_for_worker(app):
    test_worker = worker.Worker(app=app, name="foo")
    expected = job_context.JobContext(app=app, worker_id=3, worker_name="foo")

    context = test_worker.context_for_worker(worker_id=3)

    assert context == expected


def test_context_for_worker_kwargs(app):
    test_worker = worker.Worker(app=app, name="foo")
    expected = job_context.JobContext(app=app, worker_id=3, worker_name="bar")

    context = test_worker.context_for_worker(worker_id=3, worker_name="bar")

    assert context == expected


def test_context_for_worker_value_kept(app):
    test_worker = worker.Worker(app=app, name="foo")
    expected = job_context.JobContext(app=app, worker_id=3, worker_name="bar")

    test_worker.context_for_worker(worker_id=3, worker_name="bar")
    context = test_worker.context_for_worker(worker_id=3)

    assert context == expected


def test_context_for_worker_reset(app):
    test_worker = worker.Worker(app=app, name="foo")
    expected = job_context.JobContext(app=app, worker_id=3, worker_name="foo")

    test_worker.context_for_worker(worker_id=3, worker_name="bar")
    context = test_worker.context_for_worker(worker_id=3, reset=True)

    assert context == expected
