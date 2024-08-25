from __future__ import annotations

import pytest

from procrastinate import job_context
from procrastinate.app import App


@pytest.mark.parametrize(
    "job_result, expected",
    [
        (job_context.JobResult(), None),
        (job_context.JobResult(start_timestamp=10), 20),
        (job_context.JobResult(start_timestamp=10, end_timestamp=15), 5),
    ],
)
def test_job_result_duration(job_result, expected):
    assert job_result.duration(current_timestamp=30) == expected


@pytest.mark.parametrize(
    "job_result, expected",
    [
        (job_context.JobResult(), {}),
        (
            job_context.JobResult(start_timestamp=10),
            {
                "start_timestamp": 10,
                "duration": 15,
            },
        ),
        (
            job_context.JobResult(start_timestamp=10, end_timestamp=15, result="foo"),
            {
                "start_timestamp": 10,
                "end_timestamp": 15,
                "duration": 5,
                "result": "foo",
            },
        ),
    ],
)
def test_job_result_as_dict(job_result, expected, mocker):
    mocker.patch("time.time", return_value=25)
    assert job_result.as_dict() == expected


def test_evolve(app: App, job_factory):
    job = job_factory()
    context = job_context.JobContext(
        app=app, job=job, worker_name="a", should_abort=lambda: False
    )
    assert context.evolve(worker_name="b").worker_name == "b"


def test_job_description_job_no_time(app: App, job_factory):
    job = job_factory(task_name="some_task", id=12, task_kwargs={"a": "b"})
    descr = job_context.JobContext(
        worker_name="a", job=job, app=app, should_abort=lambda: False
    ).job_description(current_timestamp=0)
    assert descr == "worker: some_task[12](a='b')"


def test_job_description_job_time(app: App, job_factory):
    job = job_factory(task_name="some_task", id=12, task_kwargs={"a": "b"})
    descr = job_context.JobContext(
        worker_name="a",
        job=job,
        app=app,
        job_result=job_context.JobResult(start_timestamp=20.0),
        should_abort=lambda: False,
    ).job_description(current_timestamp=30.0)
    assert descr == "worker: some_task[12](a='b') (started 10.000 s ago)"
