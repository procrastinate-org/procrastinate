import pendulum
import pytest

from procrastinate import exceptions, jobs, tasks, worker

pytestmark = pytest.mark.asyncio


@pytest.fixture
def test_worker(app):
    return worker.Worker(app, queues=None)


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
    mocker, test_worker, job_factory, connector, side_effect, status
):
    async def coro(*args, **kwargs):
        pass

    test_worker.run_job = mocker.Mock(side_effect=side_effect or coro)
    job = job_factory(id=1)
    await test_worker.job_store.defer_job(job)

    await test_worker.process_job(job=job)

    test_worker.run_job.assert_called_with(
        job=job, log_context={"job": job.get_context()}
    )
    assert connector.jobs[1]["status"] == status


async def test_process_job_retry_failed_job(
    mocker, test_worker, job_factory, connector
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

    test_worker.run_job.assert_called_with(
        job=job, log_context={"job": job.get_context()}
    )
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
        task_name="task_func",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    await test_worker.run_job(job=job, log_context={"job": job.get_context()})

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
        task_name="task_func",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    await test_worker.run_job(job=job, log_context={"job": job.get_context()})

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
        task_name="task_func",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    await test_worker.run_job(job=job, log_context={"job": job.get_context()})

    assert result == [12]

    records = [record for record in caplog.records if record.action == "job_success"]
    assert len(records) == 1
    record = records[0]
    assert record.result == 12


@pytest.mark.parametrize(
    "worker_name, logger_name, record_worker_name",
    [(None, "worker", None), ("w1", "worker.w1", "w1")],
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
    assert all(record.name.endswith(logger_name) for record in records)
    assert all(
        getattr(record, "worker_name", None) == record_worker_name for record in records
    )


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
        task_name="job",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    with pytest.raises(exceptions.JobError):
        await test_worker.run_job(job=job, log_context={"job": job.get_context()})


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
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    with pytest.raises(exceptions.JobRetry):
        await test_worker.run_job(job=job, log_context={"job": job.get_context()})


async def test_run_job_not_found(app):
    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="job",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    with pytest.raises(exceptions.TaskNotFound):
        await test_worker.run_job(job=job, log_context={"job": job.get_context()})
