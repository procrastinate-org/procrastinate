from typing import Optional, Union

import attr
import pendulum

from cabbage import exceptions


@attr.dataclass(kw_only=True)
class RetryStrategy:
    max_attempts: Optional[int] = None
    wait: int = 0

    def get_retry_exception(self, attempts: int) -> Optional[exceptions.JobRetry]:
        schedule_in = self.get_schedule_in(attempts=attempts)
        if schedule_in is None:
            return None

        schedule_at = pendulum.now("UTC").add(seconds=schedule_in)
        return exceptions.JobRetry(schedule_at)

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
