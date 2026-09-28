"""
Procrastinate's job lifecycle, checked with due-work-harness.

due-work-harness (https://github.com/gigaverse-app/due-work-harness) is a pytest
plugin that checks background work is neither lost nor run twice. A contract
names the guarantees a system offers, out of six profiles (A to F), and binds
each claimed one to real code; the harness then generates the test cases.

This contract binds procrastinate itself, through its Django integration and a
real task defined below:

* profile B (ownership): a worker registers and fetches a job the way
  procrastinate's worker does, heartbeats keep the job its own, and
  ``retry_stalled_jobs`` gives a job back once its worker stops heartbeating.
  One case is a strict xfail: once a job is given back and fetched by another
  worker, the first worker's ``finish_job`` or ``retry_job`` still applies
  (#1633).
* profile D (retention): ``delete_old_jobs``, which the builtin
  ``remove_old_jobs`` task runs, deletes old finished jobs and keeps jobs still
  owed, however old.
* bounded retry: a task with a ``RetryStrategy`` that keeps failing runs once,
  then ``max_attempts`` more times, through ``manage.py procrastinate worker``,
  then stays failed.

The other profiles are declined or not applicable, and each says why.

The harness needs Python 3.12+; on older versions this directory is skipped.
Run it like the rest of the suite, against PostgreSQL from the PG* variables::

    uv run pytest tests/integration/contrib/django/due_work
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator

import pytest
from django.db import connection
from due_work_harness import (
    Adoption,
    BoundedRetry,
    Claim,
    Decline,
    DueWorkContract,
    FencedOwnership,
    NotApplicable,
    Profile,
    Retention,
    SafetyContract,
    SafetyProfile,
    due_work_contract_suite,
)
from due_work_harness.integrations import procrastinate as integration
from due_work_harness.integrations.procrastinate import django_worker_once

from procrastinate import JobContext, RetryStrategy
from procrastinate.contrib.django import app

QUEUE = "due_work_harness"

#: The task's executions that reached its external call, per job, and whether
#: that call fails.
EXTERNAL_CALLS: Counter[int] = Counter()
FAILING = {"external call": False}

#: Two retries: three executions, then failed. The hour's wait keeps a retried
#: job out of the current worker pass, so each pass runs the job once.
RETRY = RetryStrategy(max_attempts=2, wait=3600)


@app.task(queue=QUEUE, pass_context=True, retry=RETRY)
def call_external_service(context: JobContext) -> None:
    # EXTERNAL SEAM: the call a real task would make to another service.
    EXTERNAL_CALLS[context.job.id] += 1
    if FAILING["external call"]:
        raise ConnectionError("the external service is down")


@pytest.fixture(autouse=True)
def fresh_state(django_db_blocker) -> Iterator[None]:
    EXTERNAL_CALLS.clear()
    FAILING["external call"] = False
    yield
    # Procrastinate's models are unmanaged, so pytest-django's flush after a
    # transactional case leaves its tables alone.
    with django_db_blocker.unblock(), connection.cursor() as cursor:
        cursor.execute(
            "TRUNCATE procrastinate_events, procrastinate_jobs, procrastinate_workers CASCADE"
        )


def defer_job() -> int:
    return call_external_service.defer()


def ownership() -> FencedOwnership:
    # ARRANGE: jobs deferred through call_external_service (defer_job).
    # REAL PRODUCTION: procrastinate's register_worker, fetch_job, finish_job, retry_job, heartbeat, and retry_stalled_jobs.
    # EXTERNAL SEAM: none; the integration ages a worker's heartbeat to stand for its death.
    # OBSERVE: the job's status and worker, and that worker's last heartbeat.
    return integration.ownership(app, defer=defer_job, queue=QUEUE)


def retention() -> Retention:
    # ARRANGE: an owed job and a finished one, both older than the retention window.
    # REAL PRODUCTION: procrastinate's delete_old_jobs, which the builtin remove_old_jobs task runs.
    # EXTERNAL SEAM: none.
    # OBSERVE: whether each job still exists.
    return integration.retention(app, defer=defer_job, max_hours=24)


def _failing_job() -> int:
    FAILING["external call"] = True
    return defer_job()


def _todo_jobs() -> list[int]:
    return [job.id for job in app.job_manager.list_jobs(queue=QUEUE, status="todo")]


def _job(job_id: int) -> tuple[str, int]:
    (job,) = app.job_manager.list_jobs(id=job_id)
    return job.status, job.attempts


def _make_due(job_id: int) -> None:
    # The retry's wait has passed, on the database's clock, which fetch_job reads.
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE procrastinate_jobs SET scheduled_at = NOW() - INTERVAL '1 second' "
            "WHERE id = %s AND status = 'todo'",
            [job_id],
        )


def bounded_retry() -> BoundedRetry:
    # ARRANGE: a job whose external call keeps failing (_failing_job); only the retry's wait is skipped (_make_due).
    # REAL PRODUCTION: `manage.py procrastinate worker --one-shot`, which applies the task's RetryStrategy.
    # EXTERNAL SEAM: the task's external call, which fails and is counted (EXTERNAL_CALLS).
    # OBSERVE: the job's status and attempts, from procrastinate's list_jobs.
    return BoundedRetry(
        name="call_external_service",
        # max_attempts counts retries, after the first execution.
        max_executions=RETRY.max_attempts + 1,
        make_failing=_failing_job,
        due_work=_todo_jobs,
        run_once=django_worker_once([QUEUE]),
        advance_to_due=_make_due,
        is_terminal=lambda job_id: _job(job_id)[0] == "failed",
        failure_attempt_count=lambda job_id: EXTERNAL_CALLS[job_id],
        observe=_job,
    )


NAME = "procrastinate jobs"

JOBS = DueWorkContract(
    name=NAME,
    # Legacy only for profile B's gap, #1633.
    adoption=Adoption.LEGACY,
    transactional=True,
    profiles={
        Profile.A: Decline(
            "the worker polls the job table, so a lost notification never strands a job, and "
            "procrastinate_fetch_job claims a job as it selects it, so there is no separate owed state "
            "for a sweep to find. Giving back a dead worker's job is profile B"
        ),
        Profile.B: Claim(
            gaps={
                "assert_stale_token_is_rejected": (
                    "finish_job and retry_job update a job by id without checking its worker: a worker "
                    "presumed dead, whose job was given back and fetched by another worker, can still mark "
                    "it finished, or send it back to todo to run a second time, while the new worker runs "
                    "it (https://github.com/procrastinate-org/procrastinate/issues/1633)"
                )
            }
        ),
        Profile.C: Decline(
            "procrastinate runs jobs at least once: fetching a job counts an attempt, but whether an attempt "
            "that died reached the service its task calls is known only to the task, so a job given back "
            "by retry_stalled_jobs runs again"
        ),
        Profile.D: Claim(),
        Profile.E: NotApplicable(
            "procrastinate stores no task results; a job's only outcome is its status, which the worker "
            "writes through finish_job and retry_job, covered by profile B"
        ),
        Profile.F: Decline(
            "a job exists because the application deferred it; procrastinate derives no job from other "
            "database state"
        ),
    },
    ownership=ownership,
    retention=retention,
    safety=SafetyContract(
        name=NAME,
        profiles={
            SafetyProfile.REPLAY_SAFE_EXECUTION: Decline(
                "a job can run more than once (a retry, or retry_stalled_jobs after a worker's death), "
                "so rerunning must be safe, but that is a property of each task's code, not of "
                "procrastinate"
            ),
            SafetyProfile.BOUNDED_RETRY: Claim(),
        },
        retry=bounded_retry,
        transactional=True,
    ),
)


@due_work_contract_suite(JOBS)
class TestJobLifecycle:
    pass
