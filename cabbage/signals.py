import logging
import signal
from contextlib import contextmanager
from types import FrameType
from typing import Callable

logger = logging.getLogger(__name__)

Signals = signal.Signals


@contextmanager
def on_stop(callback: Callable[[signal.Signals, FrameType], None]):
    sigint_handler = signal.getsignal(signal.SIGINT)
    sigterm_handler = signal.getsignal(signal.SIGTERM)

    try:
        logger.debug(
            "Installing signal handler", extra={"action": "install_signal_handlers"}
        )
        signal.signal(signal.SIGINT, callback)
        signal.signal(signal.SIGTERM, callback)

        yield
    finally:
        logger.debug(
            "Resetting previous signal handler",
            extra={"action": "uninstall_signal_handlers"},
        )
        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigterm_handler)
