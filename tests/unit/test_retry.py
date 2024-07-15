from __future__ import annotations

import datetime

import pytest

from procrastinate import BaseRetryStrategy, RetryDecision, exceptions, utils
from procrastinate import retry as retry_module
from procrastinate.jobs import Job


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
    assert (
        strategy.get_schedule_in(exception=Exception(), attempts=attempts)
        == schedule_in
    )


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
def test_get_retry_decision(
    attempts, schedule_in, wait, linear_wait, exponential_wait, mocker
):
    strategy = retry_module.RetryStrategy(
        max_attempts=10,
        wait=wait,
        linear_wait=linear_wait,
        exponential_wait=exponential_wait,
    )
    job_mock = mocker.Mock(attempts=attempts)
    assert strategy.get_retry_decision(
        exception=Exception(), job=job_mock
    ) == RetryDecision(should_retry=schedule_in is not None, schedule_in=schedule_in)


@pytest.mark.parametrize(
    "exception, expected",
    [
        (ValueError(), 0),
        (KeyError(), None),
    ],
)
def test_get_schedule_in_exception(exception, expected):
    strategy = retry_module.RetryStrategy(retry_exceptions=[ValueError])
    assert strategy.get_schedule_in(exception=exception, attempts=0) == expected


@pytest.mark.parametrize(
    "exception, expected",
    [
        (ValueError(), 0),
        (KeyError(), None),
    ],
)
def test_get_retry_decision_exception(exception, expected, mocker):
    strategy = retry_module.RetryStrategy(retry_exceptions=[ValueError])
    job_mock = mocker.Mock(attempts=0)
    retry_decision = strategy.get_retry_decision(exception=exception, job=job_mock)
    assert retry_decision.should_retry == (expected is not None)
    assert retry_decision.schedule_in == expected


def test_get_retry_exception_returns_none(mocker):
    strategy = retry_module.RetryStrategy(max_attempts=10, wait=5)
    job_mock = mocker.Mock(attempts=100)
    assert strategy.get_retry_exception(exception=Exception(), job=job_mock) is None


def test_get_retry_exception_returns(mocker):
    strategy = retry_module.RetryStrategy(max_attempts=10, wait=5)

    now = utils.utcnow()
    expected = now + datetime.timedelta(seconds=5, microseconds=0)

    job_mock = mocker.Mock(attempts=1)
    exc = strategy.get_retry_exception(exception=Exception(), job=job_mock)
    assert isinstance(exc, exceptions.JobRetry)
    assert exc.scheduled_at == expected.replace(microsecond=0)


def test_custom_retry_strategy_returns(mocker):
    class CustomRetryStrategy(BaseRetryStrategy):
        def get_retry_decision(
            self, *, exception: BaseException, job: Job
        ) -> RetryDecision:
            return RetryDecision(should_retry=True, schedule_in=5, new_priority=7)

    strategy = CustomRetryStrategy()

    now = utils.utcnow()
    expected = now + datetime.timedelta(seconds=5, microseconds=0)

    job_mock = mocker.Mock(attempts=1)
    exc = strategy.get_retry_exception(exception=Exception(), job=job_mock)
    assert isinstance(exc, exceptions.JobRetry)
    assert exc.scheduled_at == expected.replace(microsecond=0)
    assert exc.new_priority == 7


def test_custom_retry_strategy_depreciated_returns_none(mocker):
    class CustomRetryStrategy(BaseRetryStrategy):
        def get_schedule_in(
            self, *, exception: BaseException, attempts: int
        ) -> int | None:
            return None

    strategy = CustomRetryStrategy()

    job_mock = mocker.Mock(attempts=1)
    with pytest.warns(
        DeprecationWarning,
        match="`get_schedule_in` is deprecated, use `get_retry_decision` instead.",
    ):
        assert strategy.get_retry_exception(exception=Exception(), job=job_mock) is None


def test_custom_retry_strategy_depreciated_returns(mocker):
    class CustomRetryStrategy(BaseRetryStrategy):
        def get_schedule_in(
            self, *, exception: BaseException, attempts: int
        ) -> int | None:
            return 5

    strategy = CustomRetryStrategy()

    now = utils.utcnow()
    expected = now + datetime.timedelta(seconds=5, microseconds=0)

    job_mock = mocker.Mock(attempts=1)
    with pytest.warns(
        DeprecationWarning,
        match="`get_schedule_in` is deprecated, use `get_retry_decision` instead.",
    ):
        exc = strategy.get_retry_exception(exception=Exception(), job=job_mock)
    assert isinstance(exc, exceptions.JobRetry)
    assert exc.scheduled_at == expected.replace(microsecond=0)
