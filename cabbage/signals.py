import signal
from contextlib import contextmanager
from typing import Any, Callable


@contextmanager
def on_stop(callback: Callable[[int, Any], None]) -> None:
    sigint_handler = signal.getsignal(signal.SIGINT)
    sigterm_handler = signal.getsignal(signal.SIGTERM)

    try:
        signal.signal(signal.SIGINT, callback)
        signal.signal(signal.SIGTERM, callback)

        yield
    finally:
        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigterm_handler)
