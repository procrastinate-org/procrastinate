import pendulum
import pytest

from procrastinate import exceptions, job_context, jobs, tasks, worker

pytestmark = pytest.mark.asyncio


@pytest.fixture
def test_worker(app):
    return worker.Worker(app, queues=None)


@pytest.fixture
def context():
    def _(job):
        return job_context.JobContext(worker_name="worker", job=job)

    return _


async def test_run(test_worker, mocker, caplog):
    caplog.set_level("INFO")

    single_worker = mocker.Mock()

    async def mock():
        single_worker()

    test_worker.single_worker = mock

    await test_worker.run()

    single_worker.assert_called()

    assert caplog.messages == [
        "Starting worker on all queues",
        "Stopped worker on all queues",
    ]


@pytest.mark.parametrize(
    "side_effect, status",
    [
        (None, "succeeded"),
        (exceptions.JobError(), "failed"),
        (exceptions.TaskNotFound(), "failed"),
    ],
)
async def test_process_job(
    mocker, test_worker, job_factory, connector, side_effect, status, context
):
    async def coro(*args, **kwargs):
        pass

    test_worker.run_job = mocker.Mock(side_effect=side_effect or coro)
    job = job_factory(id=1)
    await test_worker.job_store.defer_job(job)

    await test_worker.process_job(job=job)

    test_worker.run_job.assert_called_with(
        job=job, context=context(job=job),
    )
    assert connector.jobs[1]["status"] == status


async def test_process_job_retry_failed_job(
    mocker, test_worker, job_factory, connector, context
):
    async def coro(*args, **kwargs):
        pass

    scheduled_at = pendulum.datetime(2000, 1, 1, tz="UTC")
    test_worker.run_job = mocker.Mock(
        side_effect=exceptions.JobRetry(scheduled_at=scheduled_at)
    )
    job = job_factory(id=1)
    await test_worker.job_store.defer_job(job)

    await test_worker.process_job(job=job)

    test_worker.run_job.assert_called_with(job=job, context=context(job=job))
    assert connector.jobs[1]["status"] == "todo"
    assert connector.jobs[1]["scheduled_at"] == scheduled_at


async def test_run_job(app, context):
    result = []

    @app.task(queue="yay", name="task_func")
    def task_func(a, b):
        result.append(a + b)

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="task_func",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    await test_worker.run_job(job=job, context=context(job=job))

    assert result == [12]


async def test_run_job_async(app, context):
    result = []

    @app.task(queue="yay", name="task_func")
    async def task_func(a, b):
        result.append(a + b)

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="task_func",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    await test_worker.run_job(job=job, context=context(job=job))

    assert result == [12]


async def test_run_job_log_result(caplog, app, context):
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
        task_name="task_func",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    await test_worker.run_job(job=job, context=context(job=job))

    assert result == [12]

    records = [record for record in caplog.records if record.action == "job_success"]
    assert len(records) == 1
    record = records[0]
    assert record.result == 12


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

    worker_names = [getattr(record, "worker_name", None) for record in records]
    assert all([name == record_worker_name for name in worker_names])


async def test_run_job_error(app, context):
    def job(a, b):  # pylint: disable=unused-argument
        raise ValueError("nope")

    task = tasks.Task(job, app=app, queue="yay", name="job")
    task.func = job

    app.tasks = {"job": task}

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="job",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    with pytest.raises(exceptions.JobError):
        await test_worker.run_job(job=job, context=context(job=job))


async def test_run_job_retry(app, context):
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
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    with pytest.raises(exceptions.JobRetry):
        await test_worker.run_job(job=job, context=context(job=job))


async def test_run_job_not_found(app, context):
    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="job",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    with pytest.raises(exceptions.TaskNotFound):
        await test_worker.run_job(job=job, context=context(job=job))


async def test_run_job_pass_context(app):
    result = []

    @app.task(queue="yay", name="job", pass_context=True)
    def task_func(test_context, a):
        result.extend([test_context, a])

    job = jobs.Job(
        id=16, task_kwargs={"a": 1}, lock="sherlock", task_name="job", queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"], name="my_worker")
    context = job_context.JobContext(
        worker_name="my_worker", worker_queues=["yay"], job=job, task=task_func,
    )
    await test_worker.run_job(job=job, context=context)

    assert result == [
        context,
        1,
    ]


async def test_wait_for_job_with_job(app, mocker):
    test_worker = worker.Worker(app, timeout=42)
    # notify_event is set to None initially, and we skip run()
    test_worker.notify_event = mocker.Mock()

    wait_for = mocker.Mock()

    async def mock(coro, timeout):
        wait_for(coro, timeout=timeout)

    mocker.patch("asyncio.wait_for", mock)

    await test_worker.wait_for_job()

    wait_for.assert_called_with(test_worker.notify_event.wait.return_value, timeout=42)

    assert test_worker.notify_event.mock_calls == [
        mocker.call.clear(),
        mocker.call.wait(),
        mocker.call.clear(),
    ]


async def test_wait_for_job_without_job(app, mocker):
    test_worker = worker.Worker(app, timeout=42)
    # notify_event is set to None initially, and we skip run()
    test_worker.notify_event = mocker.Mock()

    wait_for = mocker.Mock(side_effect=TimeoutError)

    async def mock(coro, timeout):
        wait_for(coro, timeout=timeout)

    mocker.patch("asyncio.wait_for", mock)

    await test_worker.wait_for_job()

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

        async def wait_for_job(self):
            wait_for_job()

    await TestWorker(app=app, wait=False).single_worker()

    assert process_job.called is False
    assert wait_for_job.called is False


async def test_single_worker_stop_during_execution(app, mocker):
    process_job = mocker.Mock()
    wait_for_job = mocker.Mock()

    await app.configure_task("bla").defer_async()

    class TestWorker(worker.Worker):
        async def process_job(self, job):
            process_job(job=job)
            self.stop_requested = True

        async def wait_for_job(self):
            wait_for_job()

    await TestWorker(app=app).single_worker()

    assert wait_for_job.called is False
    process_job.assert_called_once()


async def test_single_worker_stop_during_wait(app, mocker):
    process_job = mocker.Mock()
    wait_for_job = mocker.Mock()

    await app.configure_task("bla").defer_async()

    class TestWorker(worker.Worker):
        async def process_job(self, job):
            process_job(job=job)

        async def wait_for_job(self):
            wait_for_job()
            self.stop_requested = True

    await TestWorker(app=app).single_worker()

    process_job.assert_called_once()
    wait_for_job.assert_called_once()
