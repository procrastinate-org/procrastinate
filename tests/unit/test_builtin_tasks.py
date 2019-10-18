import pytest

from procrastinate import builtin_tasks

pytestmark = pytest.mark.asyncio


async def test_remove_old_jobs(job_store):

    await builtin_tasks.remove_old_jobs(
        job_store, max_hours=2, queue="queue_a", remove_error=True
    )
    assert job_store.queries == [
        (
            "delete_old_jobs",
            {"nb_hours": 2, "queue": "queue_a", "statuses": ("succeeded", "failed")},
        )
    ]
