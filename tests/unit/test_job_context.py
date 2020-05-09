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
