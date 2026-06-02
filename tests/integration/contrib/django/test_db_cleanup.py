from __future__ import annotations

import asyncio
import time

import pytest
from django.db import connection

import procrastinate.contrib.django
from procrastinate.contrib.django import models


def count_other_sessions() -> int:
    """
    Number of sessions on the test database other than the test's own
    connection. The connection leaked by a worker thread (a different thread than
    the test) is invisible to Django's thread-local cache but shows up here,
    because pg_stat_activity is server-side and global.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT count(*) FROM pg_stat_activity "
            "WHERE datname = current_database() AND pid <> pg_backend_pid()"
        )
        return cursor.fetchone()[0]


def assert_no_leaked_session(before: int, timeout: float = 10.0) -> None:
    """
    Assert the worker run didn't leak a session, tolerating transient sessions.

    The worker uses its own psycopg connection pool (``min_size=4`` + listen/notify)
    whose connections are torn down asynchronously when the worker stops, so right
    after ``run_worker_once()`` the count can still be briefly elevated. A *real*
    per-thread Django ORM leak, by contrast, never goes away (the asgiref worker
    thread persists holding it). So poll until the transient pool sessions drain:
    a leak never settles and the assertion fails at the deadline.
    """
    deadline = time.monotonic() + timeout
    while count_other_sessions() > before and time.monotonic() < deadline:
        time.sleep(0.1)
    assert count_other_sessions() <= before


def run_worker_once() -> None:
    app = procrastinate.contrib.django.app

    async def run() -> None:
        # The Django connector can't listen/notify, so the worker uses a separate
        # async connector whose own pool is closed when open_async() exits.
        with app.replace_connector(app.connector.get_worker_connector()) as worker_app:
            async with worker_app.open_async():
                await worker_app.run_worker_async(
                    wait=False,
                    install_signal_handlers=False,
                    listen_notify=False,
                )

    asyncio.run(run())


# transaction=True so the deferred job is actually committed and visible to the
# worker's separate connection (a transaction-rollback test would hide it and the
# worker would process nothing, passing vacuously).
@pytest.mark.django_db(transaction=True)
def test_sync_task_does_not_leak_db_connections():
    app = procrastinate.contrib.django.app

    @app.task(name="test_db_cleanup_sync_task")
    def sync_task():
        # Sync ORM call: opens a per-thread Django connection in the worker thread.
        list(models.ProcrastinateJob.objects.all())

    sync_task.defer()

    # Assert the worker run doesn't *increase* the session count: a leaked
    # connection shows up as a net +1, while sessions left by other tests (or
    # cleaned up by our own before/after close) cancel out. An absolute count is
    # too brittle because this database is shared across the test session.
    before = count_other_sessions()
    run_worker_once()
    assert_no_leaked_session(before)


@pytest.mark.django_db(transaction=True)
def test_async_task_does_not_leak_db_connections():
    app = procrastinate.contrib.django.app

    @app.task(name="test_db_cleanup_async_task")
    async def async_task():
        # Async ORM call.
        await models.ProcrastinateJob.objects.acount()

    async_task.defer()

    before = count_other_sessions()
    run_worker_once()
    assert_no_leaked_session(before)
