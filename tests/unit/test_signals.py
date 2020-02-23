import asyncio
import signal

import pytest

from procrastinate import signals


@pytest.mark.parametrize("one_signal", [signal.SIGINT, signal.SIGTERM])
def test_on_stop(one_signal, kill_own_pid):
    called = []

    def stop():
        called.append(True)

    before = signal.getsignal(one_signal)

    with signals.on_stop(callback=stop):
        kill_own_pid(signal=one_signal)

    assert called == [True]
    assert signal.getsignal(one_signal) is before


def test_do_nothing_on_secondary_thread(mocker):
    mocker.patch("threading.main_thread", return_value=None)
    signal = mocker.patch("signal.signal")

    def stop():
        pass

    with signals.on_stop(callback=stop):
        pass

    signal.assert_not_called()


def test_on_stop_signal_twice(kill_own_pid):
    with pytest.raises(KeyboardInterrupt):
        with signals.on_stop(callback=lambda: None):
            kill_own_pid(signal=signal.SIGINT)
            kill_own_pid(signal=signal.SIGINT)


@pytest.mark.asyncio
def test_on_stop_work_with_asyncio(kill_own_pid):
    # In this test, we want to make sure that interacting with synchronisation
    # primitives from within a signal handler works.
    event = asyncio.Event()

    def stop():
        event.set()

    async def wait_and_kill():
        await asyncio.sleep(0.001)
        kill_own_pid()

    try:
        with signals.on_stop():
            asyncio.create_task(wait_and_kill())
            await asyncio.wait_for(event.wait(), timeout=0.01)
    except asyncio.TimeoutError:
        pytest.fail("Signal did not awake coroutine")
