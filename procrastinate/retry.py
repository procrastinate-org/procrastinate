"""
A retry strategy class lets procrastinate know what to do when a job fails: should it
try again? And when?
"""

from typing import Optional, Union

import attr
import pendulum

from procrastinate import exceptions


class BaseRetryStrategy:
    """
    If you want to implement your own retry strategy, you can inherit from this class.
    Children classes only need to implement `get_schedule_in`.
    """

    def get_retry_exception(self, attempts: int) -> Optional[exceptions.JobRetry]:
        schedule_in = self.get_schedule_in(attempts=attempts)
        if schedule_in is None:
            return None

        schedule_at = pendulum.now("UTC").add(seconds=schedule_in)
        return exceptions.JobRetry(schedule_at)

    def get_schedule_in(self, attempts: int) -> Optional[int]:
        """
        Parameters
        ----------
        attempts:
            The number of previous attempts for the current job. The first time
            a job is ran, `attempts` will be 0.

        Returns
        -------
        Optional[int]
            If a job should not be retried, this function should return None.
            Otherwise, it should return the duration after which to schedule the
            new job run, *in seconds*.
        """
        raise NotImplementedError()


@attr.dataclass(kw_only=True)
class RetryStrategy(BaseRetryStrategy):
    """
    The RetryStrategy class should handle simple retry strategies.

    Parameters
    ----------
    max_attempts:
        The maximum number of attempts the job should be retried
    wait:
        The number of seconds to wait between attempts
    """

    max_attempts: Optional[int] = None
    wait: int = 0

    def get_schedule_in(self, attempts: int) -> Optional[int]:
        if self.max_attempts and attempts >= self.max_attempts:
            return None

        return self.wait


RetryValue = Union[bool, int, RetryStrategy]


def get_retry_strategy(retry: RetryValue) -> Optional[RetryStrategy]:
    if not retry:
        return None

    if retry is True:
        return RetryStrategy()

    if isinstance(retry, int):
        return RetryStrategy(max_attempts=retry)

    return retry
