import signal

import pytest

from procrastinate import signals


@pytest.mark.parametrize("one_signal", [signal.SIGINT, signal.SIGTERM])
def test_on_stop(one_signal, kill_own_pid):
    called = []

    def stop(*args):
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
