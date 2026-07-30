"""
test_risk_manager.py

Contains unit tests for the RiskManager class used by the
Aladdin Forex Trading Assistant.

Author: Tharindu Kothalwala
Project: Aladdin
"""

import pytest

from app.core.exceptions import RiskError
from app.risk.risk_manager import RiskManager

# ==========================================
# Risk Amount Tests
# ==========================================


def test_calculate_risk_amount():
    """
    Test risk amount calculation using a valid balance
    and risk percentage.
    """

    risk_amount = RiskManager.calculate_risk_amount(
        account_balance=10000,
        risk_percent=1,
    )

    assert risk_amount == pytest.approx(100)


def test_calculate_risk_amount_rejects_invalid_account_balance():
    """
    Test that a zero account balance is rejected.
    """

    with pytest.raises(
        RiskError,
        match="Account balance must be greater than zero.",
    ):
        RiskManager.calculate_risk_amount(
            account_balance=0,
            risk_percent=1,
        )


def test_calculate_risk_amount_rejects_invalid_risk_percent():
    """
    Test that a zero risk percentage is rejected.
    """

    with pytest.raises(
        RiskError,
        match="Risk percentage must be between 0 and 100.",
    ):
        RiskManager.calculate_risk_amount(
            account_balance=10000,
            risk_percent=0,
        )


# ==========================================
# Position Size Tests
# ==========================================


def test_calculate_position_size():
    """
    Test the basic position-size calculation.
    """

    position_size = RiskManager.calculate_position_size(
        risk_amount=100,
        stop_loss_distance=0.0050,
    )

    assert position_size == pytest.approx(20000)


def test_calculate_position_size_rejects_zero_stop_loss_distance():
    """
    Test that a zero stop-loss distance is rejected.
    """

    with pytest.raises(
        RiskError,
        match="Stop loss distance must be greater than zero.",
    ):
        RiskManager.calculate_position_size(
            risk_amount=100,
            stop_loss_distance=0,
        )


# ==========================================
# Pip Size Tests
# ==========================================


def test_get_pip_size_for_eurusd():
    """
    Test the standard pip size for EUR/USD.
    """

    pip_size = RiskManager.get_pip_size("EUR/USD")

    assert pip_size == pytest.approx(0.0001)


def test_get_pip_size_for_usdjpy():
    """
    Test the standard pip size for USD/JPY.
    """

    pip_size = RiskManager.get_pip_size("USD/JPY")

    assert pip_size == pytest.approx(0.01)


# ==========================================
# Pip Distance Tests
# ==========================================


def test_calculate_pips_for_eurusd():
    """
    Test pip calculation for EUR/USD.
    """

    pips = RiskManager.calculate_pips(
        symbol="EUR/USD",
        price_distance=0.0050,
    )

    assert pips == pytest.approx(50)


def test_calculate_pips_for_usdjpy():
    """
    Test pip calculation for USD/JPY.
    """

    pips = RiskManager.calculate_pips(
        symbol="USD/JPY",
        price_distance=0.50,
    )

    assert pips == pytest.approx(50)


# ==========================================
# Risk-to-Reward Ratio Tests
# ==========================================


def test_calculate_risk_reward_ratio_for_buy_trade():
    """
    Test risk-to-reward calculation for a Buy trade.
    """

    ratio = RiskManager.calculate_risk_reward_ratio(
        entry_price=1.1000,
        stop_loss_price=1.0980,
        take_profit_price=1.1060,
    )

    assert ratio == pytest.approx(3.0)


def test_calculate_risk_reward_ratio_for_sell_trade():
    """
    Test risk-to-reward calculation for a Sell trade.
    """

    ratio = RiskManager.calculate_risk_reward_ratio(
        entry_price=1.1000,
        stop_loss_price=1.1020,
        take_profit_price=1.0940,
    )

    assert ratio == pytest.approx(3.0)


def test_calculate_risk_reward_ratio_rejects_zero_risk():
    """
    Test that equal entry and stop-loss prices are rejected.
    """

    with pytest.raises(
        RiskError,
        match="Entry price and stop loss cannot be equal.",
    ):
        RiskManager.calculate_risk_reward_ratio(
            entry_price=1.1000,
            stop_loss_price=1.1000,
            take_profit_price=1.1060,
        )
