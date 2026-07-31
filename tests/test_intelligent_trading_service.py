"""
test_intelligent_trading_service.py

Tests AI powered trading workflow.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.services.trading_service import (
    TradingService,
)


def test_intelligent_trade_setup_buy():

    result = TradingService.generate_intelligent_trade_setup(
        ema_signal="BULLISH",
        rsi_value=65,
        adx_value=30,
        volatility="NORMAL",
        currency="USD",
        event_type="Interest Rate Decision",
        importance="HIGH",
        sentiment="BULLISH",
    )

    assert result["market_intelligence"].market_bias == "BULLISH"

    assert result["decision"].action == "BUY"

    assert result["decision"].confidence > 70


def test_intelligent_trade_setup_hold():

    result = TradingService.generate_intelligent_trade_setup(
        ema_signal="BULLISH",
        rsi_value=50,
        adx_value=15,
        volatility="HIGH",
        currency="USD",
        event_type="Economic Report",
        importance="HIGH",
        sentiment="BEARISH",
    )

    assert result["decision"].action == "HOLD"
