"""
test_ai_reason_integration.py

Tests AI reasoning integration
with complete AI trading workflow.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from types import SimpleNamespace

from app.services.trading_service import (
    TradingService,
)


def test_ai_reason_integration(monkeypatch):

    fake_intelligence = SimpleNamespace(
        market_bias="BULLISH",
        confidence=82.0,

        technical_summary=(
            "Technical analysis supports a bullish setup."
        ),

        news_summary=(
            "News conditions are supportive."
        ),

        structure_summary=(
            "Market structure confirms bullish continuation."
        ),

        risk_level="LOW",
        recommendation="Bullish opportunity",

        structure_direction="BULLISH",
        structure_confirmation="BOS_BULLISH",

        timeframe_alignment="FULL",
        timeframe_confidence=100.0,

        timeframe_summary=(
            "Higher and lower timeframes are aligned bullish."
        ),

        market_session="LONDON",
        session_activity="HIGH",
        session_condition="FAVORABLE",

        session_summary=(
            "London session activity is favorable."
        ),
    )

    fake_analysis_result = {
        "intelligence": fake_intelligence,
    }

    class FakeMarketIntelligenceService:
        def analyze(self, symbol):
            return fake_analysis_result

        def close(self):
            pass

    monkeypatch.setattr(
        "app.services.trading_service.MarketIntelligenceService",
        FakeMarketIntelligenceService,
    )

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

    assert len(
        reasoning.technical_reason
    ) > 0

    assert len(
        reasoning.news_reason
    ) > 0

    assert len(
        reasoning.structure_reason
    ) > 0

    assert len(
        reasoning.risk_reason
    ) > 0

    assert len(
        reasoning.timeframe_reason
    ) > 0

    assert len(
        reasoning.session_reason
    ) > 0

    assert len(
        reasoning.gate_reason
    ) > 0