"""
test_ai_reason_integration.py

Tests AI reasoning integration
with complete AI trading workflow.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.services.trading_service import (
    TradingService,
)


def test_ai_reason_integration():

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

    assert "reasoning" in result

    reasoning = result["reasoning"]

    assert reasoning.decision == "BUY"

    assert reasoning.confidence > 0

    assert len(reasoning.technical_reason) > 0

    assert len(reasoning.news_reason) > 0

    assert len(reasoning.structure_reason) > 0

    assert len(reasoning.risk_reason) > 0
