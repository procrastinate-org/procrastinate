import pytest

from procrastinate import builtin_tasks, job_context

pytestmark = pytest.mark.asyncio


async def test_remove_old_jobs(app):

    await builtin_tasks.remove_old_jobs(
        job_context.JobContext(app=app), max_hours=2, queue="queue_a", remove_error=True
    )
    assert app.connector.queries == [
        (
            "delete_old_jobs",
            {"nb_hours": 2, "queue": "queue_a", "statuses": ("succeeded", "failed")},
        )
    ]
