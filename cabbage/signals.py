import logging
import signal
import threading
from contextlib import contextmanager
from types import FrameType
from typing import Callable

logger = logging.getLogger(__name__)

Signals = signal.Signals


@contextmanager
def on_stop(callback: Callable[[signal.Signals, FrameType], None]):
    if threading.current_thread() is not threading.main_thread():
        logger.debug(
            "Skipping signal handling, because this is not the main thread",
            extra={"action": "skip_signal_handlers"},
        )
        yield
        return

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
