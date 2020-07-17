import datetime

import pytest

from procrastinate import exceptions
from procrastinate import retry as retry_module
from procrastinate import utils


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
    "attempts, wait, linear_wait, exponential_wait, schedule_in",
    [
        # No wait
        (0, 0.0, 0.0, 0.0, 0.0),
        # Constant, first try
        (1, 5.0, 0.0, 0.0, 5.0),
        # Constant, last try
        (9, 5.0, 0.0, 0.0, 5.0),
        # Constant, first non-retry
        (10, 5.0, 0.0, 0.0, None),
        # Constant, other non-retry
        (100, 5.0, 0.0, 0.0, None),
        # Linear (3 * 7)
        (3, 0.0, 7.0, 0.0, 21.0),
        # Exponential (2 ** (5+1))
        (5, 0.0, 0.0, 2.0, 64.0),
        # Mix & match 8 + 3*4 + 2**(4+1) = 52
        (4, 8.0, 3.0, 2.0, 52.0),
    ],
)
def test_get_schedule_in_time(
    attempts, schedule_in, wait, linear_wait, exponential_wait
):
    strategy = retry_module.RetryStrategy(
        max_attempts=10,
        wait=wait,
        linear_wait=linear_wait,
        exponential_wait=exponential_wait,
    )
    assert strategy.get_schedule_in(exception=None, attempts=attempts) == schedule_in


@pytest.mark.parametrize(
    "exception, expected", [(ValueError(), 0), (KeyError(), None)],
)
def test_get_schedule_in_exception(exception, expected):
    strategy = retry_module.RetryStrategy(retry_exceptions=[ValueError])
    assert strategy.get_schedule_in(exception=exception, attempts=0) == expected


def test_get_retry_exception_returns_none():
    strategy = retry_module.RetryStrategy(max_attempts=10, wait=5.0)
    assert strategy.get_retry_exception(exception=None, attempts=100) is None


def test_get_retry_exception_returns():
    strategy = retry_module.RetryStrategy(max_attempts=10, wait=5.0)

    now = utils.utcnow()
    expected = now + datetime.timedelta(seconds=5, microseconds=0)

    exc = strategy.get_retry_exception(exception=None, attempts=1)
    assert isinstance(exc, exceptions.JobRetry)
    assert exc.scheduled_at == expected.replace(microsecond=0)
