from __future__ import annotations

from typing import cast

from procrastinate import builtin_tasks, job_context
from procrastinate.app import App
from procrastinate.testing import InMemoryConnector


async def test_remove_old_jobs(app: App, job_factory):
    job = job_factory()
    await builtin_tasks.remove_old_jobs(
        job_context.JobContext(app=app, job=job, should_abort=lambda: False),
        max_hours=2,
        queue="queue_a",
        remove_failed=True,
        remove_cancelled=True,
        remove_aborted=True,
    )

    connector = cast(InMemoryConnector, app.connector)
    assert connector.queries == [
        (
            "delete_old_jobs",
            {
                "nb_hours": 2,
                "queue": "queue_a",
                "statuses": ["succeeded", "failed", "cancelled", "aborted"],
            },
        )
    ]
