from __future__ import annotations

import datetime

import pytest

from procrastinate import BaseRetryStrategy, RetryDecision, exceptions, utils
from procrastinate import retry as retry_module
from procrastinate.jobs import Job

from .. import conftest


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


def test_retry_decision_constructor():
    now = conftest.aware_datetime(2000, 1, 1, tz_offset=1)
    with pytest.raises(ValueError) as exc_info:
        RetryDecision(
            retry_in={"seconds": 42},
            retry_at=now + datetime.timedelta(seconds=42, microseconds=0),
        )
    assert str(exc_info.value) == "Cannot set both retry_at and retry_in"


@pytest.mark.parametrize(
    "attempts, wait, linear_wait, exponential_wait, retry_in",
    [
        # No wait
        (0, 0.0, 0.0, 0.0, 0.0),
        # Constant, first try
        (1, 5.0, 0.0, 0.0, 5.0),
        # Constant, last try
        (9, 5.0, 0.0, 0.0, 5.0),
        # Linear (3 * 7)
        (3, 0.0, 7.0, 0.0, 21.0),
        # Exponential (2 ** (5+1))
        (5, 0.0, 0.0, 2.0, 64.0),
        # Mix & match 8 + 3*4 + 2**(4+1) = 52
        (4, 8.0, 3.0, 2.0, 52.0),
    ],
)
def test_get_retry_decision(
    attempts, wait, linear_wait, exponential_wait, retry_in, mocker
):
    now = conftest.aware_datetime(2000, 1, 1, tz_offset=1)
    mocker.patch.object(utils, "utcnow", return_value=now)
    expected = now + datetime.timedelta(seconds=retry_in, microseconds=0)

    strategy = retry_module.RetryStrategy(
        max_attempts=10,
        wait=wait,
        linear_wait=linear_wait,
        exponential_wait=exponential_wait,
    )

    job_mock = mocker.Mock(attempts=attempts)
    retry_decision = strategy.get_retry_decision(exception=Exception(), job=job_mock)
    assert isinstance(retry_decision, RetryDecision)
    assert retry_decision.retry_at == expected.replace(microsecond=0)


@pytest.mark.parametrize(
    "attempts, wait, linear_wait, exponential_wait",
    [
        # Constant, first non-retry
        (10, 5.0, 0.0, 0.0),
        # Constant, other non-retry
        (100, 5.0, 0.0, 0.0),
    ],
)
def test_get_none_retry_decision(attempts, wait, linear_wait, exponential_wait, mocker):
    strategy = retry_module.RetryStrategy(
        max_attempts=10,
        wait=wait,
        linear_wait=linear_wait,
        exponential_wait=exponential_wait,
    )
    job_mock = mocker.Mock(attempts=attempts)
    assert strategy.get_retry_decision(exception=Exception(), job=job_mock) is None


def test_get_retry_decision_does_not_overflow(mocker):
    # 5 ** 20s exceeds year 9999, the maximum representable by datetime.
    # `retry_at` should be clamped to the maximum instead of crashing.
    strategy = retry_module.RetryStrategy(exponential_wait=5)
    job_mock = mocker.Mock(attempts=20)
    retry_decision = strategy.get_retry_decision(exception=Exception(), job=job_mock)
    assert isinstance(retry_decision, RetryDecision)
    assert retry_decision.retry_at
    assert retry_decision.retry_at.year == 9999


def test_retry_exception(mocker):
    strategy = retry_module.RetryStrategy(retry_exceptions=[ValueError])
    job_mock = mocker.Mock(attempts=0)
    retry_decision = strategy.get_retry_decision(exception=ValueError(), job=job_mock)
    assert isinstance(retry_decision, RetryDecision)


def test_non_retry_exception(mocker):
    strategy = retry_module.RetryStrategy(retry_exceptions=[ValueError])
    job_mock = mocker.Mock(attempts=0)
    retry_decision = strategy.get_retry_decision(exception=KeyError(), job=job_mock)
    assert retry_decision is None


def test_get_retry_exception_returns_none(mocker):
    strategy = retry_module.RetryStrategy(max_attempts=10, wait=5)
    job_mock = mocker.Mock(attempts=100)
    assert strategy.get_retry_exception(exception=Exception(), job=job_mock) is None


def test_get_retry_exception_returns(mocker):
    now = conftest.aware_datetime(2000, 1, 1, tz_offset=1)
    mocker.patch.object(utils, "utcnow", return_value=now)
    expected = now + datetime.timedelta(seconds=5, microseconds=0)

    strategy = retry_module.RetryStrategy(max_attempts=10, wait=5)

    job_mock = mocker.Mock(attempts=1)
    exc = strategy.get_retry_exception(exception=Exception(), job=job_mock)
    assert isinstance(exc, exceptions.JobRetry)
    assert exc.retry_decision.retry_at == expected.replace(microsecond=0)


def test_custom_retry_strategy_returns(mocker):
    now = conftest.aware_datetime(2000, 1, 1, tz_offset=1)
    mocker.patch.object(utils, "utcnow", return_value=now)
    expected = now + datetime.timedelta(seconds=5, microseconds=0)

    class CustomRetryStrategy(BaseRetryStrategy):
        def get_retry_decision(
            self, *, exception: BaseException, job: Job
        ) -> RetryDecision:
            return RetryDecision(
                retry_in={"seconds": 5},
                priority=7,
                queue="some_queue",
                lock="some_lock",
            )

    strategy = CustomRetryStrategy()

    job_mock = mocker.Mock(attempts=1)
    exc = strategy.get_retry_exception(exception=Exception(), job=job_mock)
    assert isinstance(exc, exceptions.JobRetry)
    assert exc.retry_decision.retry_at == expected.replace(microsecond=0)
    assert exc.retry_decision.priority == 7
    assert exc.retry_decision.queue == "some_queue"
    assert exc.retry_decision.lock == "some_lock"


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
    now = conftest.aware_datetime(2000, 1, 1, tz_offset=1)
    mocker.patch.object(utils, "utcnow", return_value=now)
    expected = now + datetime.timedelta(seconds=5, microseconds=0)

    class CustomRetryStrategy(BaseRetryStrategy):
        def get_schedule_in(
            self, *, exception: BaseException, attempts: int
        ) -> int | None:
            return 5

    strategy = CustomRetryStrategy()

    job_mock = mocker.Mock(attempts=1)
    with pytest.warns(
        DeprecationWarning,
        match="`get_schedule_in` is deprecated, use `get_retry_decision` instead.",
    ):
        exc = strategy.get_retry_exception(exception=Exception(), job=job_mock)
    assert isinstance(exc, exceptions.JobRetry)
    assert exc.retry_decision.retry_at == expected.replace(microsecond=0)


def test_missing_implementation_of_custom_retry_strategy(mocker):
    class CustomRetryStrategy(BaseRetryStrategy):
        pass

    strategy = CustomRetryStrategy()
    job_mock = mocker.Mock(attempts=1)
    with pytest.raises(NotImplementedError) as exc_info:
        strategy.get_retry_exception(exception=Exception(), job=job_mock)
    assert str(exc_info.value) == "Missing implementation of 'get_retry_decision'."
