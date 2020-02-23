import asyncio
import logging
import signal
import threading
import types
from contextlib import contextmanager
from typing import Callable

logger = logging.getLogger(__name__)

# A few things about signals and asyncio:
# - https://docs.python.org/3/library/asyncio-eventloop.html#unix-signals
# - If you don't use loop.add_signal_handler, your handler has no effect on the queue
# - asyncio signal primitives don't give you a way to get the current handler for a
#   signal
# - If a signal has an asyncio handler, its "standard handler (installed through
#   signal.signal) is ignored (you can't get it, you can't set one, it doesn't get
#   called on the signal).
# - asyncio handlers receive no parameter
# This all mean we have to save the previous signals before installing ours, and for
# uninstalling, we need to remove the async handler and only then re-add the normal
# one. And hope that there was no previously set async handler.


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
    loop = asyncio.get_running_loop()

    def uninstall_and_callback() -> None:
        loop.remove_signal_handler(signal.SIGINT)
        loop.remove_signal_handler(signal.SIGTERM)
        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigterm_handler)
        callback()

    try:
        logger.debug(
            "Installing signal handler", extra={"action": "install_signal_handlers"}
        )
        loop.add_signal_handler(signal.SIGINT, uninstall_and_callback)
        loop.add_signal_handler(signal.SIGTERM, uninstall_and_callback)

        yield
    finally:
        logger.debug(
            "Resetting previous signal handler",
            extra={"action": "uninstall_signal_handlers"},
        )
        loop.remove_signal_handler(signal.SIGINT)
        loop.remove_signal_handler(signal.SIGTERM)
        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigterm_handler)
