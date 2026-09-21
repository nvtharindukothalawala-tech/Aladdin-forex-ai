"""
test_execution_safety_service.py

Tests for Aladdin deterministic pre-execution safety validation.

These tests do not connect to MT5 and do not send broker orders.

Author: Tharindu Kothalawala
Project: Aladdin
"""

import pytest

from app.services.execution_safety_service import (
    ExecutionSafetyService,
)


# ==========================================================
# TEST DATA
# ==========================================================


def valid_buy_setup():
    return {
        "status": "TRADE",
        "direction": "BUY",
        "targets": [
            {
                "name": "TP1",
                "price": 1.1100,
                "rr": 2.0,
            },
        ],
    }


def valid_sell_setup():
    return {
        "status": "TRADE",
        "direction": "SELL",
        "targets": [
            {
                "name": "TP1",
                "price": 1.0900,
                "rr": 2.0,
            },
        ],
    }


def valid_buy_risk():
    return {
        "status": "APPROVED",
        "approved": True,
        "engine": "DETERMINISTIC",
        "equity": 10000.0,
        "risk_percent": 1.0,
        "risk_amount": 100.0,
        "entry_price": 1.1000,
        "stop_loss": 1.0950,
        "volume": 0.20,
        "estimated_loss": 100.0,
    }


def valid_sell_risk():
    return {
        "status": "APPROVED",
        "approved": True,
        "engine": "DETERMINISTIC",
        "equity": 10000.0,
        "risk_percent": 1.0,
        "risk_amount": 100.0,
        "entry_price": 1.1000,
        "stop_loss": 1.1050,
        "volume": 0.20,
        "estimated_loss": 100.0,
    }


def valid_quote():
    return {
        "bid": 1.09950,
        "ask": 1.09960,
    }


def valid_symbol_info():
    return {
        "volume_min": 0.01,
        "volume_max": 100.0,
        "volume_step": 0.01,
    }


def analyze(
    *,
    trade_setup=None,
    risk=None,
    quote=None,
    symbol_info=None,
    execution_mode="MOCK",
    demo_execution_enabled=False,
    max_volume=10.0,
    max_spread_stop_ratio=0.25,
):
    return ExecutionSafetyService.analyze(
        trade_setup=(
            valid_buy_setup()
            if trade_setup is None
            else trade_setup
        ),
        risk=(
            valid_buy_risk()
            if risk is None
            else risk
        ),
        quote=(
            valid_quote()
            if quote is None
            else quote
        ),
        symbol_info=(
            valid_symbol_info()
            if symbol_info is None
            else symbol_info
        ),
        execution_mode=execution_mode,
        demo_execution_enabled=(
            demo_execution_enabled
        ),
        max_volume=max_volume,
        max_spread_stop_ratio=(
            max_spread_stop_ratio
        ),
    )


# ==========================================================
# VALID BUY
# ==========================================================


def test_valid_buy_is_approved():
    result = analyze()

    assert result["status"] == "APPROVED"
    assert result["approved"] is True
    assert result["engine"] == "DETERMINISTIC"

    assert result["checks"] == {
        "setup": "PASS",
        "risk": "PASS",
        "prices": "PASS",
        "spread": "PASS",
        "volume": "PASS",
        "broker_volume": "PASS",
        "environment": "PASS",
    }

    assert result["reasons"] == []


# ==========================================================
# VALID SELL
# ==========================================================


def test_valid_sell_is_approved():
    result = analyze(
        trade_setup=valid_sell_setup(),
        risk=valid_sell_risk(),
    )

    assert result["status"] == "APPROVED"
    assert result["approved"] is True

    assert all(
        value == "PASS"
        for value in result["checks"].values()
    )


# ==========================================================
# WAIT / NON-EXECUTABLE SETUP
# ==========================================================


def test_wait_setup_is_rejected():
    setup = {
        "status": "WAIT",
        "direction": None,
        "targets": [],
    }

    result = analyze(
        trade_setup=setup,
    )

    assert result["status"] == "REJECTED"
    assert result["approved"] is False
    assert result["checks"]["setup"] == "FAIL"

    assert (
        "Trade setup is not executable."
        in result["reasons"]
    )


# ==========================================================
# INVALID DIRECTION
# ==========================================================


def test_invalid_direction_is_rejected():
    setup = valid_buy_setup()
    setup["direction"] = "HOLD"

    result = analyze(
        trade_setup=setup,
    )

    assert result["approved"] is False
    assert result["checks"]["setup"] == "FAIL"

    assert (
        "Trade direction must be BUY or SELL."
        in result["reasons"]
    )


# ==========================================================
# RISK REJECTION
# ==========================================================


def test_rejected_risk_is_rejected():
    risk = valid_buy_risk()

    risk["status"] = "REJECTED"
    risk["approved"] = False

    result = analyze(
        risk=risk,
    )

    assert result["approved"] is False
    assert result["checks"]["risk"] == "FAIL"

    assert (
        "Risk analysis has not approved this trade."
        in result["reasons"]
    )


def test_missing_risk_is_rejected():
    result = ExecutionSafetyService.analyze(
        trade_setup=valid_buy_setup(),
        risk=None,
        quote=valid_quote(),
        symbol_info=valid_symbol_info(),
        execution_mode="MOCK",
        demo_execution_enabled=False,
        max_volume=10.0,
        max_spread_stop_ratio=0.25,
    )

    assert result["approved"] is False
    assert result["checks"]["risk"] == "FAIL"


# ==========================================================
# BUY PRICE STRUCTURE
# ==========================================================


def test_invalid_buy_price_structure_is_rejected():
    risk = valid_buy_risk()

    # BUY stop must be below entry.
    risk["stop_loss"] = 1.1050

    result = analyze(
        risk=risk,
    )

    assert result["approved"] is False
    assert result["checks"]["prices"] == "FAIL"

    assert (
        "Trade price structure is invalid."
        in result["reasons"]
    )


# ==========================================================
# SELL PRICE STRUCTURE
# ==========================================================


def test_invalid_sell_price_structure_is_rejected():
    risk = valid_sell_risk()

    # SELL stop must be above entry.
    risk["stop_loss"] = 1.0950

    result = analyze(
        trade_setup=valid_sell_setup(),
        risk=risk,
    )

    assert result["approved"] is False
    assert result["checks"]["prices"] == "FAIL"


# ==========================================================
# MISSING TAKE PROFIT
# ==========================================================


def test_missing_take_profit_is_rejected():
    setup = valid_buy_setup()
    setup["targets"] = []

    result = analyze(
        trade_setup=setup,
    )

    assert result["approved"] is False
    assert result["checks"]["prices"] == "FAIL"


# ==========================================================
# EXCESSIVE SPREAD
# ==========================================================


def test_excessive_spread_is_rejected():
    risk = valid_buy_risk()

    risk["entry_price"] = 1.1000
    risk["stop_loss"] = 1.0990

    quote = {
        "bid": 1.1000,
        "ask": 1.1005,
    }

    result = analyze(
        risk=risk,
        quote=quote,
        max_spread_stop_ratio=0.25,
    )

    assert result["approved"] is False
    assert result["checks"]["spread"] == "FAIL"

    assert (
        "Spread is too large relative "
        "to stop distance."
        in result["reasons"]
    )


# ==========================================================
# INVALID QUOTE
# ==========================================================


@pytest.mark.parametrize(
    "quote",
    [
        {
            "bid": 0.0,
            "ask": 1.1000,
        },
        {
            "bid": 1.1000,
            "ask": 0.0,
        },
        {
            "bid": 1.1010,
            "ask": 1.1000,
        },
    ],
)
def test_invalid_quote_is_rejected(
    quote,
):
    result = analyze(
        quote=quote,
    )

    assert result["approved"] is False
    assert result["checks"]["spread"] == "FAIL"


# ==========================================================
# ALADDIN MAXIMUM VOLUME
# ==========================================================


def test_volume_above_aladdin_limit_is_rejected():
    risk = valid_buy_risk()

    # Similar to the large-volume case observed
    # with a very tight EURUSD stop.
    risk["volume"] = 53.19

    result = analyze(
        risk=risk,
        max_volume=10.0,
    )

    assert result["approved"] is False
    assert result["checks"]["volume"] == "FAIL"

    assert (
        "Position volume exceeds the "
        "configured Aladdin safety limit."
        in result["reasons"]
    )


def test_volume_at_aladdin_limit_is_allowed():
    risk = valid_buy_risk()
    risk["volume"] = 10.0

    result = analyze(
        risk=risk,
        max_volume=10.0,
    )

    assert result["checks"]["volume"] == "PASS"


# ==========================================================
# BROKER MINIMUM / MAXIMUM
# ==========================================================


def test_volume_below_broker_minimum_is_rejected():
    risk = valid_buy_risk()
    risk["volume"] = 0.01

    symbol_info = valid_symbol_info()
    symbol_info["volume_min"] = 0.10

    result = analyze(
        risk=risk,
        symbol_info=symbol_info,
    )

    assert result["approved"] is False

    assert (
        result["checks"]["broker_volume"]
        == "FAIL"
    )


def test_volume_above_broker_maximum_is_rejected():
    risk = valid_buy_risk()
    risk["volume"] = 2.0

    symbol_info = valid_symbol_info()
    symbol_info["volume_max"] = 1.0

    result = analyze(
        risk=risk,
        symbol_info=symbol_info,
        max_volume=10.0,
    )

    assert result["approved"] is False

    assert (
        result["checks"]["broker_volume"]
        == "FAIL"
    )


# ==========================================================
# BROKER VOLUME STEP
# ==========================================================


def test_invalid_broker_volume_step_is_rejected():
    risk = valid_buy_risk()

    risk["volume"] = 0.205

    result = analyze(
        risk=risk,
    )

    assert result["approved"] is False

    assert (
        result["checks"]["broker_volume"]
        == "FAIL"
    )

    assert (
        "Position volume does not match "
        "the broker volume step."
        in result["reasons"]
    )


def test_valid_broker_volume_step_is_allowed():
    risk = valid_buy_risk()
    risk["volume"] = 0.21

    result = analyze(
        risk=risk,
    )

    assert (
        result["checks"]["broker_volume"]
        == "PASS"
    )


# ==========================================================
# INVALID BROKER SPECIFICATIONS
# ==========================================================


@pytest.mark.parametrize(
    "field",
    [
        "volume_min",
        "volume_max",
        "volume_step",
    ],
)
def test_invalid_broker_spec_is_rejected(
    field,
):
    symbol_info = valid_symbol_info()

    symbol_info[field] = 0.0

    result = analyze(
        symbol_info=symbol_info,
    )

    assert result["approved"] is False

    assert (
        result["checks"]["broker_volume"]
        == "FAIL"
    )


def test_invalid_broker_volume_range_is_rejected():
    symbol_info = valid_symbol_info()

    symbol_info["volume_min"] = 2.0
    symbol_info["volume_max"] = 1.0

    result = analyze(
        symbol_info=symbol_info,
    )

    assert result["approved"] is False

    assert (
        result["checks"]["broker_volume"]
        == "FAIL"
    )


# ==========================================================
# MOCK MODE
# ==========================================================


def test_mock_mode_is_allowed():
    result = analyze(
        execution_mode="MOCK",
        demo_execution_enabled=False,
    )

    assert (
        result["checks"]["environment"]
        == "PASS"
    )

    assert result["approved"] is True


# ==========================================================
# DEMO MODE
# ==========================================================


def test_demo_mode_requires_safety_switch():
    result = analyze(
        execution_mode="DEMO",
        demo_execution_enabled=False,
    )

    assert result["approved"] is False

    assert (
        result["checks"]["environment"]
        == "FAIL"
    )

    assert (
        "MT5 DEMO execution safety switch "
        "is disabled."
        in result["reasons"]
    )


def test_demo_mode_allowed_when_enabled():
    result = analyze(
        execution_mode="DEMO",
        demo_execution_enabled=True,
    )

    assert (
        result["checks"]["environment"]
        == "PASS"
    )

    assert result["approved"] is True


# ==========================================================
# LIVE / UNSUPPORTED MODE
# ==========================================================


@pytest.mark.parametrize(
    "mode",
    [
        "LIVE",
        "REAL",
        "PRODUCTION",
        "",
    ],
)
def test_unsupported_execution_mode_is_rejected(
    mode,
):
    result = analyze(
        execution_mode=mode,
        demo_execution_enabled=True,
    )

    assert result["approved"] is False

    assert (
        result["checks"]["environment"]
        == "FAIL"
    )

    assert (
        "Unsupported execution mode. "
        "Only MOCK and DEMO are permitted."
        in result["reasons"]
    )


# ==========================================================
# LIMITS
# ==========================================================


def test_configured_limits_are_returned():
    result = analyze(
        max_volume=5.0,
        max_spread_stop_ratio=0.20,
    )

    assert result["limits"] == {
        "max_volume": 5.0,
        "max_spread_stop_ratio": 0.20,
    }


# ==========================================================
# DETERMINISM
# ==========================================================


def test_analysis_is_deterministic():
    first = analyze()
    second = analyze()

    assert first == second