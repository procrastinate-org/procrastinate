from __future__ import annotations

import asyncio
from typing import cast

import pytest

from procrastinate.app import App
from procrastinate.exceptions import JobAborted
from procrastinate.job_context import JobContext
from procrastinate.job_processor import JobProcessor
from procrastinate.jobs import DeleteJobCondition, Job, Status
from procrastinate.testing import InMemoryConnector


class CustomCriticalError(BaseException):
    pass


@pytest.fixture
def worker_name() -> str:
    return "worker"


# it is important to make the fixture async because
# otherwise, the queue is created outside the main event loop on python 3.8
@pytest.fixture
async def job_queue() -> asyncio.Queue[Job]:
    return asyncio.Queue(2)


@pytest.fixture
def base_context(app, worker_name):
    return JobContext(
        app=app, worker_name=worker_name, additional_context={"foo": "bar"}
    )


@pytest.fixture
def job_semaphore():
    return asyncio.Semaphore(1)


@pytest.fixture
async def job_processor(request, app, base_context, job_queue, job_semaphore):
    param = getattr(request, "param", None)

    delete_jobs = cast(str, param["delete_jobs"]) if param else None
    return JobProcessor(
        task_registry=app.tasks,
        job_manager=app.job_manager,
        base_context=base_context,
        job_queue=job_queue,
        job_semaphore=job_semaphore,
        worker_id=2,
        delete_jobs=delete_jobs or DeleteJobCondition.NEVER,
        fetch_job_condition=asyncio.Condition(),
    )


@pytest.fixture(autouse=True, scope="function")
async def running_job_processor_task(job_processor):
    task = asyncio.create_task(job_processor.run())
    yield task
    if not task.cancelled():
        task.cancel()
    try:
        await asyncio.wait_for(task, 0.1)
    except asyncio.CancelledError:
        pass
    except CustomCriticalError:
        pass


async def test_run_wait_until_cancelled(job_processor):
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(job_processor.run(), 0.1)


async def test_run_job_async(app: App, job_queue):
    result = []

    @app.task(queue="yay", name="task_func")
    async def task_func(a, b):
        result.append(a + b)

    task_func.defer(a=9, b=3)
    job = await app.job_manager.fetch_job(None)
    assert job

    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)
    assert result == [12]

    assert job.id
    status = await app.job_manager.get_job_status_async(job.id)
    assert status == Status.SUCCEEDED


async def test_run_job_status(app: App, job_queue):
    result = []

    @app.task(queue="yay", name="task_func")
    async def task_func(a, b):
        result.append(a + b)

    task_func.defer(a=9, b=3)
    job = await app.job_manager.fetch_job(None)
    assert job

    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)

    assert job.id
    status = await app.job_manager.get_job_status_async(job.id)
    assert status == Status.SUCCEEDED


async def test_run_job_sync(app: App, job_queue):
    result = []

    @app.task(queue="yay", name="task_func")
    def task_func(a, b):
        result.append(a + b)

    task_func.defer(a=9, b=3)
    job = await app.job_manager.fetch_job(None)
    assert job
    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)
    assert result == [12]


async def test_run_job_semi_async(app: App, job_queue):
    result = []

    @app.task(queue="yay", name="task_func")
    def task_func(a, b):
        async def inner():
            result.append(a + b)

        return inner()

    task_func.defer(a=9, b=3)
    job = await app.job_manager.fetch_job(None)
    assert job
    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)
    assert result == [12]


async def test_run_job_log_result(caplog, app: App, job_queue):
    caplog.set_level("INFO")

    @app.task(queue="yay", name="task_func")
    async def task_func(a, b):
        return a + b

    task_func.defer(a=9, b=3)
    job = await app.job_manager.fetch_job(None)
    assert job
    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)

    records = [record for record in caplog.records if record.action == "job_success"]
    assert len(records) == 1
    record = records[0]
    assert record.result == 12
    assert "Result: 12" in record.message


async def test_run_job_aborted(caplog, app: App, job_queue):
    caplog.set_level("INFO")

    @app.task(queue="yay", name="task_func")
    def task_func(a, b):
        raise JobAborted()

    task_func.defer(a=9, b=3)
    job = await app.job_manager.fetch_job(None)
    assert job
    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)

    records = [record for record in caplog.records if record.action == "job_aborted"]
    assert len(records) == 1
    record = records[0]
    assert record.levelname == "INFO"
    assert "Aborted" in record.message


async def test_run_job_aborted_status(app: App, job_queue):
    @app.task(queue="yay", name="task_func")
    async def task_func():
        raise JobAborted()

    task_func.defer()
    job = await app.job_manager.fetch_job(None)
    assert job

    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)

    assert job.id
    status = await app.job_manager.get_job_status_async(job.id)
    assert status == Status.ABORTED


async def test_run_job_error_log(caplog, app: App, job_queue):
    caplog.set_level("INFO")

    @app.task(queue="yay", name="task_func")
    def task_func(a, b):
        raise ValueError("Nope")

    task_func.defer(a=9, b=3)
    job = await app.job_manager.fetch_job(None)
    assert job
    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)

    records = [record for record in caplog.records if record.action == "job_error"]
    assert len(records) == 1
    record = records[0]
    assert record.levelname == "ERROR"
    assert "to retry" not in record.message


async def test_run_job_error_status(app: App, job_queue):
    @app.task(queue="yay", name="task_func")
    def task_func():
        raise ValueError("Nope")

    task_func.defer()
    job = await app.job_manager.fetch_job(None)
    assert job
    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)

    assert job.id
    status = await app.job_manager.get_job_status_async(job.id)
    assert status == Status.FAILED


@pytest.mark.parametrize(
    "critical_error",
    [
        (False),
        (True),
    ],
)
async def test_run_job_retry_failed_job(app: App, job_queue, critical_error):
    @app.task(retry=1)
    def task_func():
        raise CustomCriticalError("Nope") if critical_error else ValueError("Nope")

    task_func.defer()
    job = await app.job_manager.fetch_job(None)
    assert job
    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)

    connector = cast(InMemoryConnector, app.connector)
    assert job.id
    job_row = connector.jobs[job.id]
    assert job_row["status"] == "todo"
    assert job_row["scheduled_at"] is not None
    assert job_row["attempts"] == 1


async def test_run_job_critical_error(
    caplog, app: App, job_queue, running_job_processor_task: asyncio.Task
):
    caplog.set_level("INFO")

    @app.task(queue="yay", name="task_func")
    def task_func(a, b):
        raise CustomCriticalError("Nope")

    task_func.defer(a=9, b=3)
    job = await app.job_manager.fetch_job(None)
    assert job
    job_queue.put_nowait(job)

    with pytest.raises(BaseException, match="Nope"):
        await asyncio.wait_for(job_queue.join(), 0.1)
        await running_job_processor_task

    assert job.id
    status = await app.job_manager.get_job_status_async(job.id)
    assert status == Status.FAILED


async def test_run_task_not_found_log(caplog, app: App, job_queue):
    caplog.set_level("INFO")

    @app.task(queue="yay", name="task_func")
    def task_func(a, b):
        return a + b

    task_func.defer(a=9, b=3)
    job = await app.job_manager.fetch_job(None)
    assert job
    job = job.evolve(task_name="random_task_name")

    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)

    records = [record for record in caplog.records if record.action == "task_not_found"]
    assert len(records) == 1
    record = records[0]
    assert record.levelname == "ERROR"


async def test_run_task_not_found_status(app: App, job_queue):
    @app.task(queue="yay", name="task_func")
    def task_func():
        pass

    task_func.defer()
    job = await app.job_manager.fetch_job(None)
    assert job
    job = job.evolve(task_name="random_task_name")

    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)

    assert job.id
    status = await app.job_manager.get_job_status_async(job.id)
    assert status == Status.FAILED


async def test_worker_copy_additional_context(app: App, job_queue, base_context):
    base_context.additional_context["foo"] = "baz"

    @app.task(pass_context=True)
    async def task_func(jobContext: JobContext):
        assert jobContext.additional_context["foo"] == "bar"

    await task_func.defer_async()
    job = await app.job_manager.fetch_job(None)
    assert job

    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)


async def test_worker_pass_worker_id_to_context(app: App, job_queue, job_processor):
    assert job_processor.worker_id == 2

    @app.task(pass_context=True)
    async def task_func(jobContext: JobContext):
        assert jobContext.worker_id == 2

    await task_func.defer_async()
    job = await app.job_manager.fetch_job(None)
    assert job

    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)


@pytest.mark.parametrize(
    "job_processor, fail_task",
    [
        ({"delete_jobs": "successful"}, False),
        ({"delete_jobs": "always"}, False),
        ({"delete_jobs": "always"}, True),
    ],
    indirect=["job_processor"],
)
async def test_process_job_with_deletion(app: App, job_queue, fail_task):
    @app.task()
    async def task_func():
        if fail_task:
            raise ValueError("Nope")

    await task_func.defer_async()
    job = await app.job_manager.fetch_job(None)
    assert job

    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)

    connector = cast(InMemoryConnector, app.connector)
    assert job.id not in connector.jobs


@pytest.mark.parametrize(
    "job_processor, fail_task",
    [
        ({"delete_jobs": "never"}, False),
        ({"delete_jobs": "never"}, True),
        ({"delete_jobs": "successful"}, True),
    ],
    indirect=["job_processor"],
)
async def test_process_job_without_deletion(app: App, job_queue, fail_task):
    @app.task()
    async def task_func():
        if fail_task:
            raise ValueError("Nope")

    await task_func.defer_async()
    job = await app.job_manager.fetch_job(None)
    assert job

    job_queue.put_nowait(job)
    await asyncio.wait_for(job_queue.join(), 0.1)

    connector = cast(InMemoryConnector, app.connector)
    assert job.id in connector.jobs


@pytest.mark.parametrize(
    "fail_task",
    [
        (False),
        (True),
    ],
)
async def test_process_job_notifies_completion(
    app: App, job_queue, fail_task, running_job_processor_task, job_semaphore
):
    @app.task()
    async def task_func():
        if fail_task:
            raise ValueError("Nope")

    await task_func.defer_async()
    job = await app.job_manager.fetch_job(None)
    assert job
    job_queue.put_nowait(job)

    await asyncio.wait_for(job_semaphore.acquire(), 0.1)
    job_semaphore.release()


async def test_cancelling_processor_waits_for_task(
    app: App, job_queue, running_job_processor_task: asyncio.Task
):
    complete_task_event = asyncio.Event()

    @app.task()
    async def task_func():
        await complete_task_event.wait()

    await task_func.defer_async()
    job = await app.job_manager.fetch_job(None)
    assert job
    job_queue.put_nowait(job)

    # this should timeout because task is waiting for complete_task_event
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(job_queue.join(), 0.05)

    running_job_processor_task.cancel()

    # this should still timeout when cancelled because it is waiting for task to complete
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(job_queue.join(), 0.05)

    # tell the task to complete
    complete_task_event.set()

    # this should successfully complete the job and re-raise the CancelledError
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(running_job_processor_task, 0.1)

    assert job.id
    status = await app.job_manager.get_job_status_async(job.id)
    assert status == Status.SUCCEEDED
