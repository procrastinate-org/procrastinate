import asyncio
import logging
import signal
import sys
import threading
from contextlib import contextmanager
from typing import Any, Callable, Optional

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
        logger.warning(
            "Skipping signal handling, because this is not the main thread",
            extra={"action": "skip_signal_handlers"},
        )
        yield
        return

    sigint_handler = signal.getsignal(signal.SIGINT)
    sigterm_handler = signal.getsignal(signal.SIGTERM)

    uninstalled = False
    loop: Optional[asyncio.AbstractEventLoop]
    if sys.version_info < (3, 7):
        if asyncio.Task.current_task():
            loop = asyncio.get_event_loop()
        else:
            loop = None
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

    def uninstall_and_callback(*args) -> None:
        nonlocal uninstalled
        uninstalled = True
        uninstall(
            loop=loop, sigint_handler=sigint_handler, sigterm_handler=sigterm_handler
        )
        callback()

    try:
        install(loop=loop, handler=uninstall_and_callback)
        yield
    finally:
        if not uninstalled:
            uninstall(
                loop=loop,
                sigint_handler=sigint_handler,
                sigterm_handler=sigterm_handler,
            )


def install(loop: Optional[asyncio.AbstractEventLoop], handler: Callable):
    logger.debug(
        "Installing signal handler", extra={"action": "install_signal_handlers"}
    )
    if loop:
        loop.add_signal_handler(signal.SIGINT, handler)
        loop.add_signal_handler(signal.SIGTERM, handler)
    else:
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)


def uninstall(
    loop: Optional[asyncio.AbstractEventLoop],
    sigint_handler: Any,
    sigterm_handler: Any,
):
    logger.debug(
        "Resetting previous signal handler",
        extra={"action": "uninstall_signal_handlers"},
    )
    if loop:
        loop.remove_signal_handler(signal.SIGINT)
        loop.remove_signal_handler(signal.SIGTERM)
    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)
