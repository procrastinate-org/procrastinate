import attr
import pytest

from procrastinate import admin as admin_module
from procrastinate import jobs, store

pytestmark = pytest.mark.asyncio


@pytest.fixture
def admin(pg_connector):
    return admin_module.Admin(connector=pg_connector)


@pytest.fixture
def pg_job_store(pg_connector):
    return store.JobStore(connector=pg_connector)


@pytest.fixture(autouse=True)
async def setup(pg_job_store):
    await pg_job_store.defer_job(
        jobs.Job(
            queue="q1", lock="lock1", task_name="task_foo", task_kwargs={"key": "a"},
        )
    )

    j2 = jobs.Job(
        queue="q1", lock="lock2", task_name="task_bar", task_kwargs={"key": "b"},
    )
    j2 = attr.evolve(j2, id=await pg_job_store.defer_job(j2))
    await pg_job_store.finish_job(j2, jobs.Status.FAILED)

    j3 = jobs.Job(
        queue="q2", lock="lock3", task_name="task_foo", task_kwargs={"key": "c"},
    )
    j3 = attr.evolve(j3, id=await pg_job_store.defer_job(j3))
    await pg_job_store.finish_job(j3, jobs.Status.SUCCEEDED)


async def test_list_jobs(admin, pg_job_store):
    assert await admin.list_jobs_async() == [
        {
            "id": 1,
            "queue": "q1",
            "task": "task_foo",
            "lock": "lock1",
            "args": {"key": "a"},
            "status": "todo",
            "scheduled_at": None,
            "attempts": 0,
        },
        {
            "id": 2,
            "queue": "q1",
            "task": "task_bar",
            "lock": "lock2",
            "args": {"key": "b"},
            "status": "failed",
            "scheduled_at": None,
            "attempts": 1,
        },
        {
            "id": 3,
            "queue": "q2",
            "task": "task_foo",
            "lock": "lock3",
            "args": {"key": "c"},
            "status": "succeeded",
            "scheduled_at": None,
            "attempts": 1,
        },
    ]

    assert await admin.list_jobs_async(id=1) == [
        {
            "id": 1,
            "queue": "q1",
            "task": "task_foo",
            "lock": "lock1",
            "args": {"key": "a"},
            "status": "todo",
            "scheduled_at": None,
            "attempts": 0,
        },
    ]

    assert await admin.list_jobs_async(lock="lock3") == [
        {
            "id": 3,
            "queue": "q2",
            "task": "task_foo",
            "lock": "lock3",
            "args": {"key": "c"},
            "status": "succeeded",
            "scheduled_at": None,
            "attempts": 1,
        },
    ]

    assert await admin.list_jobs_async(queue="q1", task="task_foo") == [
        {
            "id": 1,
            "queue": "q1",
            "task": "task_foo",
            "lock": "lock1",
            "args": {"key": "a"},
            "status": "todo",
            "scheduled_at": None,
            "attempts": 0,
        },
    ]

    assert await admin.list_jobs_async(status="failed") == [
        {
            "id": 2,
            "queue": "q1",
            "task": "task_bar",
            "lock": "lock2",
            "args": {"key": "b"},
            "status": "failed",
            "scheduled_at": None,
            "attempts": 1,
        },
    ]


async def test_list_queues(admin):
    assert await admin.list_queues_async() == [
        {
            "name": "q1",
            "jobs_count": 2,
            "todo": 1,
            "doing": 0,
            "succeeded": 0,
            "failed": 1,
        },
        {
            "name": "q2",
            "jobs_count": 1,
            "todo": 0,
            "doing": 0,
            "succeeded": 1,
            "failed": 0,
        },
    ]

    assert await admin.list_queues_async(queue="q2") == [
        {
            "name": "q2",
            "jobs_count": 1,
            "todo": 0,
            "doing": 0,
            "succeeded": 1,
            "failed": 0,
        },
    ]

    assert await admin.list_queues_async(task="task_foo") == [
        {
            "name": "q1",
            "jobs_count": 1,
            "todo": 1,
            "doing": 0,
            "succeeded": 0,
            "failed": 0,
        },
        {
            "name": "q2",
            "jobs_count": 1,
            "todo": 0,
            "doing": 0,
            "succeeded": 1,
            "failed": 0,
        },
    ]

    assert await admin.list_queues_async(status="todo") == [
        {
            "name": "q1",
            "jobs_count": 1,
            "todo": 1,
            "doing": 0,
            "succeeded": 0,
            "failed": 0,
        },
    ]

    assert await admin.list_queues_async(lock="lock2") == [
        {
            "name": "q1",
            "jobs_count": 1,
            "todo": 0,
            "doing": 0,
            "succeeded": 0,
            "failed": 1,
        },
    ]


async def test_list_tasks(admin):
    assert await admin.list_tasks_async() == [
        {
            "name": "task_foo",
            "jobs_count": 2,
            "todo": 1,
            "doing": 0,
            "succeeded": 1,
            "failed": 0,
        },
        {
            "name": "task_bar",
            "jobs_count": 1,
            "todo": 0,
            "doing": 0,
            "succeeded": 0,
            "failed": 1,
        },
    ]

    assert await admin.list_tasks_async(queue="q2") == [
        {
            "name": "task_foo",
            "jobs_count": 1,
            "todo": 0,
            "doing": 0,
            "succeeded": 1,
            "failed": 0,
        },
    ]

    assert await admin.list_tasks_async(task="task_foo") == [
        {
            "name": "task_foo",
            "jobs_count": 2,
            "todo": 1,
            "doing": 0,
            "succeeded": 1,
            "failed": 0,
        },
    ]

    assert await admin.list_tasks_async(status="todo") == [
        {
            "name": "task_foo",
            "jobs_count": 1,
            "todo": 1,
            "doing": 0,
            "succeeded": 0,
            "failed": 0,
        },
    ]

    assert await admin.list_tasks_async(lock="lock2") == [
        {
            "name": "task_bar",
            "jobs_count": 1,
            "todo": 0,
            "doing": 0,
            "succeeded": 0,
            "failed": 1,
        },
    ]


@pytest.mark.parametrize("status", ["doing", "succeeded", "failed"])
async def test_set_job_status(admin, status):
    (job1,) = await admin.list_jobs_async(id=1)
    assert job1["status"] == "todo"

    await admin.set_job_status_async(1, status)
    (job1,) = await admin.list_jobs_async(id=1)
    assert job1["status"] == status
