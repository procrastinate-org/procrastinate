from __future__ import annotations

import asyncio
import datetime
import json

import freezegun
import pytest
from asgiref.sync import async_to_sync

from procrastinate import sql, types
from procrastinate.contrib.django import testing


@pytest.fixture
def django_testing_connector(db):
    return testing.DjangoTestingConnector(alias="default")


async def test_defer_job_notifies(django_testing_connector):
    event = asyncio.Event()
    received = []

    async def on_notification(*, channel: str, payload: str):
        received.append((channel, payload))
        event.set()

    await django_testing_connector.listen_notify(
        on_notification=on_notification, channels=["procrastinate_queue_v1#default"]
    )

    result = await django_testing_connector.execute_query_all_async(
        query=sql.queries["defer_jobs"],
        jobs=[
            types.JobToDefer(
                task_name="my_task",
                queue_name="default",
                lock=None,
                queueing_lock=None,
                args={},
                scheduled_at=None,
                priority=0,
            )
        ],
    )

    assert event.is_set()
    assert len(received) == 1
    channel, payload_str = received[0]
    assert channel == "procrastinate_queue_v1#default"
    payload = json.loads(payload_str)
    assert payload["type"] == "job_inserted"
    assert payload["job_id"] == result[0]["id"]


def test_defer_job_sync_notifies(django_testing_connector):
    received = []

    async def on_notification(*, channel: str, payload: str):
        received.append((channel, payload))

    async_to_sync(django_testing_connector.listen_notify)(
        on_notification=on_notification, channels=["procrastinate_queue_v1#default"]
    )

    result = django_testing_connector.execute_query_all(
        query=sql.queries["defer_jobs"],
        jobs=[
            types.JobToDefer(
                task_name="my_task",
                queue_name="default",
                lock=None,
                queueing_lock=None,
                args={},
                scheduled_at=None,
                priority=0,
            )
        ],
    )

    assert len(received) == 1
    channel, payload_str = received[0]
    assert channel == "procrastinate_queue_v1#default"
    payload = json.loads(payload_str)
    assert payload["type"] == "job_inserted"
    assert payload["job_id"] == result[0]["id"]


async def test_cancel_job_notifies(django_testing_connector):
    event = asyncio.Event()
    received = []

    async def on_notification(*, channel: str, payload: str):
        received.append((channel, payload))
        event.set()

    await django_testing_connector.listen_notify(
        on_notification=on_notification, channels=["procrastinate_queue_v1#default"]
    )

    result = await django_testing_connector.execute_query_all_async(
        query=sql.queries["defer_jobs"],
        jobs=[
            types.JobToDefer(
                task_name="my_task",
                queue_name="default",
                lock=None,
                queueing_lock=None,
                args={},
                scheduled_at=None,
                priority=0,
            )
        ],
    )

    received.clear()
    event.clear()

    await django_testing_connector.execute_query_one_async(
        query=sql.queries["cancel_job"],
        job_id=result[0]["id"],
        abort=True,
        delete_job=False,
    )

    assert event.is_set()
    assert len(received) == 1
    channel, payload_str = received[0]
    assert channel == "procrastinate_queue_v1#default"
    payload = json.loads(payload_str)
    assert payload["type"] == "abort_job_requested"
    assert payload["job_id"] == result[0]["id"]


def test_freezegun_mocking(django_testing_connector):
    queries = [
        "SELECT now()",
        "SELECT transaction_timestamp()",
        "SELECT statement_timestamp()",
        "SELECT clock_timestamp()",
    ]

    # Without freezegun, time should not be overridden
    for q in queries:
        result = django_testing_connector.execute_query_one(query=q)
        value = next(iter(result.values()))
        assert value.year != 2000

    # With freezegun, the override should be applied automatically
    frozen_time = datetime.datetime(2000, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    with freezegun.freeze_time("2000-01-01T00:00:00Z"):
        for q in queries:
            result = django_testing_connector.execute_query_one(query=q)
            value = next(iter(result.values()))
            assert value == frozen_time

    # After freezegun block, time should be back to normal
    for q in queries:
        result = django_testing_connector.execute_query_one(query=q)
        value = next(iter(result.values()))
        assert value.year != 2000
