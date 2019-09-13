import pytest

from procrastinate import postgres


@pytest.mark.parametrize(
    "queues, channels",
    [
        (["a", "b"], ["procrastinate_queue#a", "procrastinate_queue#b"]),
        (None, ["procrastinate_any_queue"]),
    ],
)
def test_channel_names(queues, channels):
    assert postgres.channel_names(queues) == channels
