"""
test_mt5_session_lock.py

Regression tests for shared MetaTrader 5 session
synchronization across Aladdin MT5 components.

The MetaTrader5 Python package maintains process-level
connection state. A market-data request must not be able
to shut down MT5 while another broker/execution request
is using the same Python process, and vice versa.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from threading import Event, Thread
from types import SimpleNamespace

import app.market.mt5_provider as provider_module
import app.mt5.mt5_connector as connector_module

from app.market.mt5_provider import MT5DataProvider
from app.mt5.mt5_connector import MT5Connector


class FakeSharedMT5:
    """
    Minimal fake MT5 module used to verify that the
    shared session lock serializes access between the
    market-data provider and the execution connector.
    """

    ACCOUNT_TRADE_MODE_DEMO = 0

    def __init__(self):
        self.initialize_calls = 0
        self.shutdown_calls = 0

    def initialize(self):
        self.initialize_calls += 1
        return True

    def shutdown(self):
        self.shutdown_calls += 1

    def last_error(self):
        return (1, "Success")

    def account_info(self):
        return SimpleNamespace(
            trade_mode=self.ACCOUNT_TRADE_MODE_DEMO,
            trade_allowed=True,
            trade_expert=True,
        )

    def terminal_info(self):
        return SimpleNamespace(
            connected=True,
        )


def test_shared_mt5_lock_serializes_provider_and_connector(
    monkeypatch,
):
    """
    While MT5DataProvider owns the shared MT5 session,
    MT5Connector.connect() must wait.

    Once the provider disconnects, the connector may
    initialize MT5 and continue. This protects against
    one request shutting down the global MT5 session
    while another request is still using it.
    """

    fake_mt5 = FakeSharedMT5()

    monkeypatch.setattr(
        provider_module,
        "mt5",
        fake_mt5,
    )

    monkeypatch.setattr(
        connector_module,
        "mt5",
        fake_mt5,
    )

    provider = MT5DataProvider()
    connector = MT5Connector(
        mode="DEMO"
    )

    provider.connect()

    assert provider.connected is True
    assert fake_mt5.initialize_calls == 1

    connector_started = Event()
    connector_finished = Event()
    connector_errors = []

    def connect_connector():
        connector_started.set()

        try:
            connector.connect()
        except Exception as exc:
            connector_errors.append(exc)
        finally:
            connector_finished.set()

    thread = Thread(
        target=connect_connector,
        daemon=True,
    )

    thread.start()

    assert connector_started.wait(
        timeout=1.0
    )

    # The connector thread must still be blocked because
    # the provider owns the shared MT5 session lock.
    assert connector_finished.wait(
        timeout=0.1
    ) is False

    assert connector.connected is False
    assert fake_mt5.initialize_calls == 1
    assert fake_mt5.shutdown_calls == 0

    provider.disconnect()

    # Releasing the provider session must allow the
    # connector to acquire the same lock and connect.
    assert connector_finished.wait(
        timeout=1.0
    )

    thread.join(
        timeout=1.0
    )

    assert connector_errors == []
    assert connector.connected is True
    assert fake_mt5.initialize_calls == 2
    assert fake_mt5.shutdown_calls == 1

    connector.disconnect()

    assert connector.connected is False
    assert fake_mt5.shutdown_calls == 2


def test_provider_connect_failure_releases_shared_lock(
    monkeypatch,
):
    """
    A provider initialization failure must not leave
    the shared MT5 lock permanently acquired.
    """

    class FailingMT5(FakeSharedMT5):

        def initialize(self):
            self.initialize_calls += 1
            return False

    failing_mt5 = FailingMT5()

    monkeypatch.setattr(
        provider_module,
        "mt5",
        failing_mt5,
    )

    provider = MT5DataProvider()

    try:
        provider.connect()
    except RuntimeError:
        pass
    else:
        raise AssertionError(
            "Provider connection failure was expected."
        )

    assert provider.connected is False
    assert provider._session_lock_acquired is False
    assert failing_mt5.shutdown_calls == 1


def test_connector_connect_failure_releases_shared_lock(
    monkeypatch,
):
    """
    A connector validation failure must clean up MT5
    and release the shared session lock.
    """

    class MissingAccountMT5(FakeSharedMT5):

        def account_info(self):
            return None

    failing_mt5 = MissingAccountMT5()

    monkeypatch.setattr(
        connector_module,
        "mt5",
        failing_mt5,
    )

    connector = MT5Connector(
        mode="DEMO"
    )

    try:
        connector.connect()
    except ConnectionError:
        pass
    else:
        raise AssertionError(
            "Connector connection failure was expected."
        )

    assert connector.connected is False
    assert connector.account_info is None
    assert connector._session_lock_acquired is False
    assert failing_mt5.shutdown_calls == 1
