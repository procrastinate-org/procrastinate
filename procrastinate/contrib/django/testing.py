from __future__ import annotations

import datetime
import json
from collections.abc import Iterable
from typing import Any

from typing_extensions import LiteralString

from procrastinate import connector, jobs, sql, utils
from procrastinate.contrib.django import django_connector


class DjangoTestingConnector(django_connector.DjangoConnector):
    """
    A testing connector for Django applications.

    While `InMemoryConnector` is useful for fast unit tests without a database,
    integration tests typically require hitting the database to test the full
    application flow. However, running a standard `PsycopgConnector` worker
    inside a Django test (which is often wrapped in a transaction) can cause
    deadlocks or fail to see uncommitted data.

    This connector exists to solve this problem. It uses the exact same database
    connection as the Django test, allowing the Procrastinate worker to run inside
    the same transaction. This means users can interact with the Procrastinate ORM
    models (e.g. `ProcrastinateJob.objects.update(...)`) to manipulate job states
    or schedules before the worker runs, providing an environment closer to reality.

    It simulates the PostgreSQL `LISTEN/NOTIFY` system in-memory since Django's
    transactional tests cannot rely on real database notifications.

    This class is primarily used by developers writing integration tests for their
    Django applications that depend on Procrastinate, often implicitly via the
    provided pytest plugin fixtures.
    """

    def __init__(self, alias: str = "default") -> None:
        super().__init__(alias=alias)
        self.on_notification: connector.Notify | None = None
        self.notify_channels: list[str] = []
        self._time_override_value: datetime.datetime | None = None

    async def listen_notify(
        self, on_notification: connector.Notify, channels: Iterable[str]
    ) -> None:
        self.on_notification = on_notification
        self.notify_channels = list(channels)

    async def _notify(self, queue_name: str, notification: jobs.Notification) -> None:
        if not self.on_notification:
            return

        destination_channels = {
            "procrastinate_any_queue_v1",
            f"procrastinate_queue_v1#{queue_name}",
        }

        for channel in set(self.notify_channels).intersection(destination_channels):
            await self.on_notification(
                channel=channel,
                payload=json.dumps(notification),
            )

    def _override_time(self, time: datetime.datetime) -> None:
        """
        Sets the database time for the current connection to a static value.
        """
        if self._time_override_value is not None and self._time_override_value == time:
            return

        time_str = time.isoformat()
        with self.connection.cursor() as cursor:
            cursor.execute(
                sql.queries["testing_override_time"].format(time_str=time_str)
            )
        self._time_override_value = time

    def _unoverride_time(self) -> None:
        """
        Drops the time-overriding functions.
        """
        if self._time_override_value is None:
            return

        with self.connection.cursor() as cursor:
            cursor.execute(sql.queries["testing_unoverride_time"])
        self._time_override_value = None

    def _check_and_apply_time_override(self) -> None:
        now = datetime.datetime.now(datetime.timezone.utc)
        is_time_frozen = type(now).__module__ != "datetime"

        if is_time_frozen:
            self._override_time(now)
        else:
            self._unoverride_time()

    @django_connector.wrap_exceptions()
    def execute_query_one(
        self, query: LiteralString, **arguments: Any
    ) -> dict[str, Any]:
        self._check_and_apply_time_override()
        result = super().execute_query_one(query, **arguments)

        if query == sql.queries["defer_periodic_job"] and result.get("id"):
            utils.async_to_sync(
                self._notify,
                queue_name=arguments["queue"],
                notification={"type": "job_inserted", "job_id": result["id"]},
            )
        elif query == sql.queries["cancel_job"] and arguments.get("abort"):
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT queue_name FROM procrastinate_jobs WHERE id = %s",
                    [arguments["job_id"]],
                )
                row = cursor.fetchone()
                if row:
                    utils.async_to_sync(
                        self._notify,
                        queue_name=row[0],
                        notification={
                            "type": "abort_job_requested",
                            "job_id": arguments["job_id"],
                        },
                    )

        return result

    def _dictfetch(self, cursor: Any):
        """
        Return all rows from a cursor as a dict.

        This method overrides the parent `_dictfetch` to handle manual JSON
        deserialization. In a production environment, Procrastinate's async
        connectors register custom `psycopg` adapters for composite types and JSONB.
        However, the Django testing connection uses the default `psycopg` adapter
        for the test database.

        As a result, JSONB columns (like the `args` column returned by `fetch_job`)
        are fetched as raw JSON strings rather than Python dictionaries. This override
        intercepts the rows as they are fetched and manually deserializes the `args`
        column.

        This exists so that the Procrastinate worker, when running in a Django test
        environment using this connector, receives properly formatted job parameters
        and does not crash when attempting to access `job.task_kwargs.items()`.
        """
        columns = [col[0] for col in cursor.description]
        return (
            {
                col: (
                    json.loads(val) if col == "args" and isinstance(val, str) else val
                )
                for col, val in zip(columns, row)
            }
            for row in cursor.fetchall()
        )

    @django_connector.wrap_exceptions()
    def execute_query(self, query: LiteralString, **arguments: Any) -> None:
        self._check_and_apply_time_override()
        super().execute_query(query, **arguments)

    @django_connector.wrap_exceptions()
    def execute_query_all(
        self, query: LiteralString, **arguments: Any
    ) -> list[dict[str, Any]]:
        self._check_and_apply_time_override()
        result = super().execute_query_all(query, **arguments)

        if query == sql.queries["defer_jobs"]:
            for i, row in enumerate(result):
                job = arguments["jobs"][i]
                if isinstance(job, dict):
                    queue_name = job["queue_name"]
                else:
                    queue_name = getattr(job, "queue_name", "default")
                utils.async_to_sync(
                    self._notify,
                    queue_name=queue_name,
                    notification={"type": "job_inserted", "job_id": row["id"]},
                )

        return result
