import pendulum
import pytest

from procrastinate import exceptions
from procrastinate import retry as retry_module


@pytest.mark.parametrize(
    "retry, expected_strategy",
    [
        (None, None),
        (12, retry_module.RetryStrategy(max_attempts=12)),
        (True, retry_module.RetryStrategy()),
        (
            retry_module.RetryStrategy(max_attempts=42),
            retry_module.RetryStrategy(max_attempts=42),
        ),
    ],
)
def test_get_retry_strategy(retry, expected_strategy):
    assert expected_strategy == retry_module.get_retry_strategy(retry)


@pytest.mark.parametrize(
    "attempts, schedule_in", [(1, 5), (9, 5), (10, None), (11, None), (100, None)]
)
def test_get_schedule_in(attempts, schedule_in):
    strategy = retry_module.RetryStrategy(max_attempts=10, wait=5)
    assert strategy.get_schedule_in(attempts=attempts) == schedule_in


def test_get_retry_exception_returns_none():
    strategy = retry_module.RetryStrategy(max_attempts=10, wait=5)
    assert strategy.get_retry_exception(attempts=100) is None


def test_get_retry_exception_returns():
    strategy = retry_module.RetryStrategy(max_attempts=10, wait=5)

    now = pendulum.datetime(2000, 1, 1, tz="UTC")
    expected = pendulum.datetime(2000, 1, 1, 0, 0, 5, tz="UTC")
    with pendulum.test(now):
        exc = strategy.get_retry_exception(attempts=1)
        assert isinstance(exc, exceptions.JobRetry)
        assert exc.scheduled_at == expected
