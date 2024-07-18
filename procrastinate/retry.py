"""
A retry strategy class lets procrastinate know what to do when a job fails: should it
try again? And when?
"""

from __future__ import annotations

import datetime
import warnings
from typing import Iterable, Union, overload

import attr

from procrastinate import exceptions, types, utils
from procrastinate.jobs import Job


class RetryDecision:
    retry_at: datetime.datetime | None = None
    priority: int | None = None
    queue: str | None = None
    lock: str | None = None

    @overload
    def __init__(
        self,
        retry_at: None = None,
        retry_in: types.TimeDeltaParams | None = None,
        priority: int | None = None,
        queue: str | None = None,
        lock: str | None = None,
    ) -> None: ...
    @overload
    def __init__(
        self,
        retry_at: datetime.datetime | None = None,
        retry_in: None = None,
        priority: int | None = None,
        queue: str | None = None,
        lock: str | None = None,
    ) -> None: ...
    def __init__(
        self,
        retry_at: datetime.datetime | None = None,
        retry_in: types.TimeDeltaParams | None = None,
        priority: int | None = None,
        queue: str | None = None,
        lock: str | None = None,
    ) -> None:
        if retry_at and retry_in is not None:
            raise ValueError("Cannot set both retry_at and retry_in")

        if retry_in is not None:
            retry_at = utils.datetime_from_timedelta_params(retry_in)

        self.retry_at = retry_at
        self.priority = priority
        self.queue = queue
        self.lock = lock


class BaseRetryStrategy:
    """
    If you want to implement your own retry strategy, you can inherit from this class.
    Child classes only need to implement `get_retry_decision`.
    """

    def get_retry_exception(
        self, exception: BaseException, job: Job
    ) -> exceptions.JobRetry | None:
        try:
            retry_decision = self.get_retry_decision(exception=exception, job=job)
            if retry_decision is None:
                return None

            return exceptions.JobRetry(retry_decision=retry_decision)
        except NotImplementedError:
            warnings.warn(
                "`get_schedule_in` is deprecated, use `get_retry_decision` instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            schedule_in = self.get_schedule_in(
                exception=exception, attempts=job.attempts
            )
            if schedule_in is None:
                return None

            retry_decision = RetryDecision(retry_in={"seconds": schedule_in})
            return exceptions.JobRetry(retry_decision)

    def get_schedule_in(self, *, exception: BaseException, attempts: int) -> int | None:
        """
        Parameters
        ----------
        attempts:
            The number of previous attempts for the current job. The first time
            a job is run, ``attempts`` will be 0.

        Returns
        -------
        ``Optional[int]``
            If a job should not be retried, this function should return None.
            Otherwise, it should return the duration after which to schedule the
            new job run, *in seconds*.

        Notes
        -----
        This function is deprecated and will be removed in a future version. Use
        `get_retry_decision` instead.
        """
        raise NotImplementedError()

    def get_retry_decision(
        self, *, exception: BaseException, job: Job
    ) -> RetryDecision | None:
        """
        Parameters
        ----------
        exception:
            The exception raised by the job
        job:
            The current job

        Returns
        -------
        ``RetryDecision``
            A RetryDecision object with the following attributes:
            - should_retry: a boolean indicating whether the job should be retried
            - schedule_in: an optional float indicating the number of seconds to wait
            - priority: an optional integer indicating the new priority of the job
        """
        raise NotImplementedError()


@attr.dataclass(kw_only=True)
class RetryStrategy(BaseRetryStrategy):
    """
    The RetryStrategy class should handle classic retry strategies.

    You can mix and match several waiting strategies. The formula is::

        total_wait = wait + lineal_wait * attempts + exponential_wait ** (attempts + 1)

    Parameters
    ----------
    max_attempts:
        The maximum number of attempts the job should be retried
    wait:
        Use this if you want to use a constant backoff.
        Give a number of seconds as argument, it will be used to compute the backoff.
        (e.g. if 3, then successive runs will wait 3, 3, 3, 3, 3 seconds)
    linear_wait:
        Use this if you want to use a linear backoff.
        Give a number of seconds as argument, it will be used to compute the backoff.
        (e.g. if 3, then successive runs will wait 0, 3, 6, 9, 12 seconds)
    exponential_wait:
        Use this if you want to use an exponential backoff.
        Give a number of seconds as argument, it will be used to compute the backoff.
        (e.g. if 3, then successive runs will wait 3, 9, 27, 81, 243 seconds)
    retry_exceptions:
        Define the exception types you want to retry on.
        If you don't, jobs will be retried on any type of exceptions

    """

    max_attempts: int | None = None
    wait: int = 0
    linear_wait: int = 0
    exponential_wait: int = 0
    retry_exceptions: Iterable[type[Exception]] | None = None

    def get_schedule_in(self, *, exception: BaseException, attempts: int) -> int | None:
        # TODO: remove this method in a future version and move logic to `get_retry_decision`
        if self.max_attempts and attempts >= self.max_attempts:
            return None
        # isinstance's 2nd param must be a tuple, not an arbitrary iterable
        if self.retry_exceptions and not isinstance(
            exception, tuple(self.retry_exceptions)
        ):
            return None
        wait: int = self.wait
        wait += self.linear_wait * attempts
        wait += self.exponential_wait ** (attempts + 1)
        return wait

    def get_retry_decision(
        self, *, exception: BaseException, job: Job
    ) -> RetryDecision | None:
        schedule_in = self.get_schedule_in(exception=exception, attempts=job.attempts)

        if schedule_in is None:
            return None

        return RetryDecision(retry_in={"seconds": schedule_in})


RetryValue = Union[bool, int, RetryStrategy]


def get_retry_strategy(retry: RetryValue) -> RetryStrategy | None:
    if not retry:
        return None

    if retry is True:
        return RetryStrategy()

    if isinstance(retry, int):
        return RetryStrategy(max_attempts=retry)

    return retry
