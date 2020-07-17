"""
A retry strategy class lets procrastinate know what to do when a job fails: should it
try again? And when?
"""
import datetime
from typing import Iterable, Optional, Type, Union

import attr

from procrastinate import exceptions, utils


class BaseRetryStrategy:
    """
    If you want to implement your own retry strategy, you can inherit from this class.
    Child classes only need to implement `get_schedule_in`.
    """

    def get_retry_exception(
        self, exception: Exception, attempts: int
    ) -> Optional[exceptions.JobRetry]:
        schedule_in = self.get_schedule_in(exception=exception, attempts=attempts)
        if schedule_in is None:
            return None

        schedule_at = utils.utcnow() + datetime.timedelta(seconds=schedule_in)
        return exceptions.JobRetry(schedule_at.replace(microsecond=0))

    def get_schedule_in(self, *, exception: Exception, attempts: int) -> Optional[int]:
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

    max_attempts: Optional[int] = None
    wait: int = 0
    linear_wait: int = 0
    exponential_wait: int = 0
    retry_exceptions: Optional[Iterable[Type[Exception]]] = None

    def get_schedule_in(self, *, exception: Exception, attempts: int) -> Optional[int]:
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


RetryValue = Union[bool, int, RetryStrategy]


def get_retry_strategy(retry: RetryValue) -> Optional[RetryStrategy]:
    if not retry:
        return None

    if retry is True:
        return RetryStrategy()

    if isinstance(retry, int):
        return RetryStrategy(max_attempts=retry)

    return retry
