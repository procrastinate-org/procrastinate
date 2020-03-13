import pendulum
import pytest

from procrastinate import exceptions, jobs, tasks, worker

pytestmark = pytest.mark.asyncio


async def test_run(app, connector):
    class TestWorker(worker.Worker):

        async def single_worker(self, notify_event):
            await notify_event.wait()

    test_worker = TestWorker(app=app, queues=["marsupilami"])

    await test_worker.run()
    test_worker.notify_task.cancel()

    assert app.connector.queries == [
        ("listen_for_jobs", "procrastinate_queue#marsupilami")
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
    mocker, app, job_factory, connector, side_effect, status
):
    job = job_factory(id=1)
    await app.job_store.defer_job(job)

    test_worker = worker.Worker(app, queues=["queue"])

    async def coro(*args, **kwargs):
        pass

    run_job = mocker.patch(
        "procrastinate.worker.Worker.run_job", side_effect=side_effect or coro
    )
    await test_worker.process_job(job)

    run_job.assert_called_once()
    assert run_job.call_args.args == ()
    assert run_job.call_args.kwargs["job"] == job
    assert "log_context" in run_job.call_args.kwargs
    assert connector.jobs[1]["status"] == status


async def test_process_job_retry_failed_job(connector, mocker, app, job_factory):
    job = job_factory(id=1)
    await app.job_store.defer_job(job)

    mocker.patch(
        "procrastinate.worker.Worker.run_job",
        side_effect=exceptions.JobRetry(
            scheduled_at=pendulum.datetime(2000, 1, 1, tz="UTC")
        ),
    )

    test_worker = worker.Worker(app, queues=["queue"])
    await test_worker.process_job(job)

    assert len(connector.jobs) == 1
    new_job = connector.jobs[1]
    assert new_job["status"] == "todo"
    assert new_job["id"] == 1
    assert new_job["scheduled_at"] == pendulum.datetime(2000, 1, 1, tz="UTC")


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
    log_context = {"worker_name": "foo", "job": job.get_context()}
    await test_worker.run_job(job, log_context)

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
    log_context = {"worker_name": "foo", "job": job.get_context()}
    await test_worker.run_job(job, log_context)

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
    log_context = {"worker_name": "foo", "job": job.get_context()}
    await test_worker.run_job(job, log_context)

    assert result == [12]

    records = [record for record in caplog.records if record.action == "job_success"]
    assert len(records) == 1
    record = records[0]
    assert record.result == 12


async def test_run_job_log_name(caplog, app):
    caplog.set_level("INFO")

    def task_func():
        pass

    task = tasks.Task(task_func, app=app, queue="yay", name="job")

    app.tasks = {"task_func": task}

    job = jobs.Job(
        id=16, task_kwargs={}, lock="sherlock", task_name="task_func", queue="yay",
    )

    test_worker = worker.Worker(app, queues=["yay"])
    log_context = {"worker_name": test_worker.worker_name, "job": job.get_context()}
    await test_worker.run_job(job, log_context)
    assert len(caplog.records) == 2
    assert all(record.name.endswith("worker") for record in caplog.records)
    assert all(record.worker_name is None for record in caplog.records)

    caplog.clear()

    test_worker = worker.Worker(app, queues=["yay"], name="w1")
    log_context = {"worker_name": test_worker.worker_name, "job": job.get_context()}
    await test_worker.run_job(job, log_context)
    assert len(caplog.records) == 2
    assert all(record.name.endswith("worker.w1") for record in caplog.records)
    assert all(record.worker_name == "w1" for record in caplog.records)


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
    log_context = {"worker_name": test_worker.worker_name, "job": job.get_context()}
    with pytest.raises(exceptions.JobError):
        await test_worker.run_job(job, log_context)


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
    log_context = {"worker_name": test_worker.worker_name, "job": job.get_context()}
    with pytest.raises(exceptions.JobRetry):
        await test_worker.run_job(job, log_context)


async def test_run_job_not_found(app):
    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="job",
        queue="yay",
    )
    test_worker = worker.Worker(app, queues=["yay"])
    log_context = {"worker_name": test_worker.worker_name, "job": job.get_context()}
    with pytest.raises(exceptions.TaskNotFound):
        await test_worker.run_job(job, log_context)
