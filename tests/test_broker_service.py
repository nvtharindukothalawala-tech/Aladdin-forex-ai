"""
test_broker_service.py

Tests the read-only MT5 BrokerService contract.

These tests verify that broker evidence required by
execution reconciliation is preserved correctly without
connecting to a real MT5 terminal.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from datetime import (
    datetime,
    timezone,
)
from types import SimpleNamespace

import app.services.broker_service as broker_module
from app.services.broker_service import BrokerService


# ======================================================
# FAKE CONNECTOR
# ======================================================


class FakeDemoConnector:
    """
    Fake DEMO connector.

    Prevents tests from connecting to a real MT5 terminal.
    """

    mode = "DEMO"

    connected = False
    disconnected = False

    def connect(self):
        type(self).connected = True

    def disconnect(self):
        type(self).disconnected = True


# ======================================================
# HELPERS
# ======================================================


def reset_fake_connector():
    """
    Reset connector state before each test.
    """

    FakeDemoConnector.connected = False
    FakeDemoConnector.disconnected = False


def make_open_position(
    *,
    ticket=123456,
    identifier=654321,
    symbol="EURUSD",
    position_type=0,
    volume=0.01,
    comment="ALADDIN E849",
):
    """
    Create fake MT5 open-position data.
    """

    return SimpleNamespace(
        ticket=ticket,
        identifier=identifier,
        symbol=symbol,
        type=position_type,
        volume=volume,
        price_open=1.10000,
        price_current=1.10100,
        sl=1.09800,
        tp=1.10400,
        profit=10.50,
        swap=-0.25,
        magic=20260911,
        comment=comment,
    )


def make_deal(
    *,
    ticket,
    order,
    position_id,
    entry,
    deal_type,
    time_value,
    symbol="EURUSD",
    volume=0.01,
    price=1.10000,
    profit=0.0,
    commission=0.0,
    swap=0.0,
    fee=0.0,
    magic=20260911,
    comment="",
):
    """
    Create fake MT5 deal data.
    """

    return SimpleNamespace(
        ticket=ticket,
        order=order,
        position_id=position_id,
        entry=entry,
        type=deal_type,
        time=time_value,
        time_msc=time_value * 1000,
        symbol=symbol,
        volume=volume,
        price=price,
        profit=profit,
        commission=commission,
        swap=swap,
        fee=fee,
        magic=magic,
        comment=comment,
    )


# ======================================================
# OPEN POSITION CONTRACT
# ======================================================


def test_get_open_positions_exposes_reconciliation_fields(
    monkeypatch,
):
    """
    Open-position monitoring must preserve the fields
    required by execution reconciliation.
    """

    reset_fake_connector()

    fake_position = make_open_position()

    fake_mt5 = SimpleNamespace(
        POSITION_TYPE_BUY=0,
        POSITION_TYPE_SELL=1,
        positions_get=lambda: (
            fake_position,
        ),
        last_error=lambda: (0, "OK"),
    )

    monkeypatch.setattr(
        broker_module,
        "MT5Connector",
        FakeDemoConnector,
    )

    monkeypatch.setattr(
        broker_module,
        "mt5",
        fake_mt5,
    )

    result = BrokerService.get_open_positions()

    assert result["execution_mode"] == "DEMO"
    assert result["connected"] is True
    assert result["position_count"] == 1

    position = result["positions"][0]

    assert position["ticket"] == 123456
    assert position["identifier"] == 654321
    assert position["symbol"] == "EURUSD"
    assert position["direction"] == "BUY"
    assert position["volume"] == 0.01
    assert position["comment"] == "ALADDIN E849"

    assert FakeDemoConnector.connected is True
    assert FakeDemoConnector.disconnected is True


def test_get_open_positions_uses_ticket_when_identifier_missing(
    monkeypatch,
):
    """
    If MT5 does not expose a separate position identifier,
    BrokerService should fall back to the position ticket.
    """

    reset_fake_connector()

    fake_position = make_open_position(
        ticket=777001,
    )

    delattr(
        fake_position,
        "identifier",
    )

    fake_mt5 = SimpleNamespace(
        POSITION_TYPE_BUY=0,
        POSITION_TYPE_SELL=1,
        positions_get=lambda: (
            fake_position,
        ),
        last_error=lambda: (0, "OK"),
    )

    monkeypatch.setattr(
        broker_module,
        "MT5Connector",
        FakeDemoConnector,
    )

    monkeypatch.setattr(
        broker_module,
        "mt5",
        fake_mt5,
    )

    result = BrokerService.get_open_positions()

    position = result["positions"][0]

    assert position["ticket"] == 777001
    assert position["identifier"] == 777001

    assert FakeDemoConnector.connected is True
    assert FakeDemoConnector.disconnected is True


# ======================================================
# CLOSED TRADE CORRELATION CONTRACT
# ======================================================


def test_trade_history_preserves_opening_correlation_data(
    monkeypatch,
):
    """
    Completed-trade history must preserve the original
    opening comment and opening broker identifiers.

    This is required because the closing deal may have
    a different or empty comment.
    """

    reset_fake_connector()

    now = int(
        datetime.now(
            timezone.utc
        ).timestamp()
    )

    position_id = 9005

    opening_deal = make_deal(
        ticket=9001,
        order=9002,
        position_id=position_id,
        entry=0,
        deal_type=0,
        time_value=now - 3600,
        symbol="GBPUSD",
        volume=0.02,
        price=1.25000,
        profit=0.0,
        commission=-0.20,
        magic=20260911,
        comment="ALADDIN E849",
    )

    closing_deal = make_deal(
        ticket=9004,
        order=9003,
        position_id=position_id,
        entry=1,
        deal_type=1,
        time_value=now - 60,
        symbol="GBPUSD",
        volume=0.02,
        price=1.25500,
        profit=20.00,
        commission=-0.20,
        swap=-0.10,
        magic=20260911,
        comment="",
    )

    class FakeMT5:
        POSITION_TYPE_BUY = 0
        POSITION_TYPE_SELL = 1

        DEAL_TYPE_BUY = 0
        DEAL_TYPE_SELL = 1

        DEAL_ENTRY_IN = 0
        DEAL_ENTRY_OUT = 1
        DEAL_ENTRY_INOUT = 2
        DEAL_ENTRY_OUT_BY = 3

        @staticmethod
        def positions_get():
            return ()

        @staticmethod
        def last_error():
            return (0, "OK")

        @staticmethod
        def history_deals_get(
            *args,
            **kwargs,
        ):
            if "position" in kwargs:
                assert kwargs["position"] == position_id

                return (
                    opening_deal,
                    closing_deal,
                )

            return (
                closing_deal,
            )

    monkeypatch.setattr(
        broker_module,
        "MT5Connector",
        FakeDemoConnector,
    )

    monkeypatch.setattr(
        broker_module,
        "mt5",
        FakeMT5,
    )

    result = BrokerService.get_trade_history(
        days=30,
    )

    assert result["execution_mode"] == "DEMO"
    assert result["connected"] is True
    assert result["closed_trade_count"] == 1

    trade = result["closed_trades"][0]

    assert trade["deal_ticket"] == 9004
    assert trade["order_ticket"] == 9003

    assert trade["opening_deal_ticket"] == 9001
    assert trade["opening_order_ticket"] == 9002

    assert trade["position_id"] == 9005
    assert trade["symbol"] == "GBPUSD"
    assert trade["direction"] == "BUY"
    assert trade["volume"] == 0.02

    # Critical reconciliation contract:
    # opening comment must be preserved even though
    # the closing deal has no correlation comment.
    assert trade["comment"] == "ALADDIN E849"

    assert trade["magic"] == 20260911
    assert trade["is_aladdin_trade"] is True

    assert FakeDemoConnector.connected is True
    assert FakeDemoConnector.disconnected is True