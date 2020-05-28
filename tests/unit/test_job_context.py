import pytest

from procrastinate import job_context


@pytest.mark.parametrize(
    "queues, result", [(None, "all queues"), (["foo", "bar"], "queues foo, bar")]
)
def test_queues_display(queues, result):
    context = job_context.JobContext(worker_queues=queues)
    assert context.queues_display == result


def test_evolve():
    context = job_context.JobContext(worker_name="a")
    assert context.evolve(worker_name="b").worker_name == "b"


def test_log_extra():
    context = job_context.JobContext(
        worker_name="a", worker_id=2, additional_context={"ha": "ho"}
    )

    assert context.log_extra(action="foo", bar="baz") == {
        "action": "foo",
        "bar": "baz",
        "ha": "ho",
        "worker": {"name": "a", "id": 2, "queues": None},
    }


def test_log_extra_job(job_factory):
    job = job_factory()
    context = job_context.JobContext(worker_name="a", worker_id=2, job=job)

    assert context.log_extra(action="foo") == {
        "action": "foo",
        "job": job.log_context(),
        "worker": {"name": "a", "id": 2, "queues": None},
    }


def test_job_description_no_job(job_factory):
    descr = job_context.JobContext(worker_name="a", worker_id=2).job_description(
        current_timestamp=0
    )
    assert descr == "worker 2: no current job"


def test_job_description_job_no_time(job_factory):
    job = job_factory(task_name="some_task", id=12, task_kwargs={"a": "b"})
    descr = job_context.JobContext(
        worker_name="a", worker_id=2, job=job
    ).job_description(current_timestamp=0)
    assert descr == "worker 2: some_task[12](a='b')"


def test_job_description_job_time(job_factory):
    job = job_factory(task_name="some_task", id=12, task_kwargs={"a": "b"})
    descr = job_context.JobContext(
        worker_name="a",
        worker_id=2,
        job=job,
        additional_context={"start_timestamp": 20.0},
    ).job_description(current_timestamp=30.0)
    assert descr == "worker 2: some_task[12](a='b') (started 10.000 s ago)"
