import attr
import pytest

from procrastinate import admin as admin_module
from procrastinate import jobs, store

pytestmark = pytest.mark.asyncio


@pytest.fixture
def admin(aiopg_connector):
    return admin_module.Admin(connector=aiopg_connector)


@pytest.fixture
def pg_job_store(aiopg_connector):
    return store.JobStore(connector=aiopg_connector)


@pytest.fixture
async def fixture_jobs(pg_job_store, job_factory):
    j1 = job_factory(
        queue="q1",
        lock="lock1",
        queueing_lock="queueing_lock1",
        task_name="task_foo",
        task_kwargs={"key": "a"},
    )
    j1 = attr.evolve(j1, id=await pg_job_store.defer_job_async(j1))

    j2 = job_factory(
        queue="q1",
        lock="lock2",
        queueing_lock="queueing_lock2",
        task_name="task_bar",
        task_kwargs={"key": "b"},
    )
    j2 = attr.evolve(j2, id=await pg_job_store.defer_job_async(j2))
    await pg_job_store.finish_job(j2, jobs.Status.FAILED)

    j3 = job_factory(
        queue="q2",
        lock="lock3",
        queueing_lock="queueing_lock3",
        task_name="task_foo",
        task_kwargs={"key": "c"},
    )
    j3 = attr.evolve(j3, id=await pg_job_store.defer_job_async(j3))
    await pg_job_store.finish_job(j3, jobs.Status.SUCCEEDED)

    return [j1, j2, j3]


async def test_list_jobs_dict(fixture_jobs, admin, pg_job_store):
    j1, *_ = fixture_jobs
    assert (await admin.list_jobs_async())[0] == {
        "id": j1.id,
        "status": "todo",
        "queue": j1.queue,
        "task": j1.task_name,
        "lock": j1.lock,
        "queueing_lock": j1.queueing_lock,
        "args": j1.task_kwargs,
        "scheduled_at": j1.scheduled_at,
        "attempts": j1.attempts,
    }


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, [1, 2, 3]),
        ({"id": 1}, [1]),
        ({"lock": "lock3"}, [3]),
        ({"queue": "q1", "task": "task_foo"}, [1]),
        ({"status": "failed"}, [2]),
        ({"queueing_lock": "queueing_lock2"}, [2]),
    ],
)
async def test_list_jobs(fixture_jobs, admin, kwargs, expected):
    assert [e["id"] for e in await admin.list_jobs_async(**kwargs)] == expected


async def test_list_queues_dict(fixture_jobs, admin):
    assert (await admin.list_queues_async())[0] == {
        "name": "q1",
        "jobs_count": 2,
        "todo": 1,
        "doing": 0,
        "succeeded": 0,
        "failed": 1,
    }


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, ["q1", "q2"]),
        ({"queue": "q2"}, ["q2"]),
        ({"task": "task_foo"}, ["q1", "q2"]),
        ({"status": "todo"}, ["q1"]),
        ({"lock": "lock2"}, ["q1"]),
    ],
)
async def test_list_queues(fixture_jobs, admin, kwargs, expected):
    assert [e["name"] for e in await admin.list_queues_async(**kwargs)] == expected


async def test_list_tasks_dict(fixture_jobs, admin):
    assert (await admin.list_tasks_async())[0] == {
        "name": "task_bar",
        "jobs_count": 1,
        "todo": 0,
        "doing": 0,
        "succeeded": 0,
        "failed": 1,
    }


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, ["task_bar", "task_foo"]),
        ({"queue": "q2"}, ["task_foo"]),
        ({"task": "task_foo"}, ["task_foo"]),
        ({"status": "todo"}, ["task_foo"]),
        ({"lock": "lock2"}, ["task_bar"]),
    ],
)
async def test_list_tasks(fixture_jobs, admin, kwargs, expected):
    assert [e["name"] for e in await admin.list_tasks_async(**kwargs)] == expected


@pytest.mark.parametrize("status", ["doing", "succeeded", "failed"])
async def test_set_job_status(fixture_jobs, admin, status):
    await admin.set_job_status_async(1, status)
    (job1,) = await admin.list_jobs_async(id=1)
    assert job1["status"] == status
