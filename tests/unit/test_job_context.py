import pytest

from procrastinate import job_context


@pytest.mark.parametrize(
    "queues, result", [(None, "all queues"), (["foo", "bar"], "queues foo, bar")]
)
def test_queues_display(queues, result):
    context = job_context.JobContext(worker_queues=queues)
    assert context.queues_display == result
