"""
test_ai_trade_setup.py

Tests complete AI trade setup workflow.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.services.trading_service import (
    TradingService,
)


def test_ai_trade_setup_buy():

    result = TradingService.generate_ai_trade_setup(
        symbol="EUR/USD",
        ema_signal="BULLISH",
        rsi_value=65,
        adx_value=30,
        volatility="NORMAL",
        currency="USD",
        event_type="Interest Rate Decision",
        importance="HIGH",
        sentiment="BULLISH",
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1150,
        account_balance=10000,
        risk_percent=1,
        trade_risk_amount=100,
        lot_size=0.10,
    )

    assert result["decision"].action == "BUY"

    assert result["market_intelligence"].market_bias == "BULLISH"

    assert "trade_plan" in result

    assert "risk_validation" in result

    assert "approval" in result


def test_ai_trade_setup_hold():

    result = TradingService.generate_ai_trade_setup(
        symbol="EUR/USD",
        ema_signal="BULLISH",
        rsi_value=50,
        adx_value=10,
        volatility="HIGH",
        currency="USD",
        event_type="Economic Report",
        importance="HIGH",
        sentiment="BEARISH",
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1150,
        account_balance=10000,
        risk_percent=1,
        trade_risk_amount=100,
        lot_size=0.10,
    )

    assert result["decision"].action == "HOLD"
