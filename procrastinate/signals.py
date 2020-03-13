import logging
import signal
import threading
import types
from contextlib import contextmanager
from typing import Callable

logger = logging.getLogger(__name__)


@contextmanager
def on_stop(callback: Callable[[], None]):
    if threading.current_thread() is not threading.main_thread():
        logger.debug(
            "Skipping signal handling, because this is not the main thread",
            extra={"action": "skip_signal_handlers"},
        )
        yield
        return

    sigint_handler = signal.getsignal(signal.SIGINT)
    sigterm_handler = signal.getsignal(signal.SIGTERM)

    def uninstall_and_callback(signum: signal.Signals, frame: types.FrameType) -> None:
        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigterm_handler)
        callback()

    try:
        logger.debug(
            "Installing signal handler", extra={"action": "install_signal_handlers"}
        )
        signal.signal(signal.SIGINT, uninstall_and_callback)
        signal.signal(signal.SIGTERM, uninstall_and_callback)

        yield
    finally:
        logger.debug(
            "Resetting previous signal handler",
            extra={"action": "uninstall_signal_handlers"},
        )
        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigterm_handler)
