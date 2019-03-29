import signal
from contextlib import contextmanager
from types import FrameType
from typing import Callable

Signals = signal.Signals


@contextmanager
def on_stop(callback: Callable[[signal.Signals, FrameType], None]):
    sigint_handler = signal.getsignal(signal.SIGINT)
    sigterm_handler = signal.getsignal(signal.SIGTERM)

    try:
        signal.signal(signal.SIGINT, callback)
        signal.signal(signal.SIGTERM, callback)

        yield
    finally:
        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigterm_handler)
