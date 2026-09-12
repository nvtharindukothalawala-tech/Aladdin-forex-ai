"""
test_ai_trade_setup.py

Tests complete AI trade setup workflow.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from types import SimpleNamespace

from app.services.trading_service import TradingService


def install_bullish_low_risk_intelligence(monkeypatch):
    """
    Replace live market intelligence with a deterministic
    bullish setup for unit testing.
    """

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


def test_ai_trade_setup_buy(monkeypatch):
    """
    Test that a safe bullish market setup
    produces a BUY decision.
    """

    install_bullish_low_risk_intelligence(
        monkeypatch,
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

    assert result["decision"].approved is True

    assert (
        result["market_intelligence"].market_bias
        == "BULLISH"
    )

    assert "trade_plan" in result

    assert "risk_validation" in result

    assert (
        result["risk_validation"].approved
        is True
    )

    assert "approval" in result

    assert (
        result["approval"].approved
        is True
    )

    assert "reasoning" in result


def test_ai_trade_setup_hold(monkeypatch):
    """
    Test that unsafe backend market intelligence
    produces a HOLD decision and stops the workflow.
    """

    fake_intelligence = SimpleNamespace(
        market_bias="BULLISH",
        confidence=80.0,

        technical_summary=(
            "Technical conditions are mixed."
        ),
        news_summary=(
            "News conditions are uncertain."
        ),
        structure_summary=(
            "Structure is bullish but risk is elevated."
        ),

        risk_level="MEDIUM",
        recommendation="Wait",

        structure_direction="BULLISH",
        structure_confirmation="BOS_BULLISH",

        timeframe_alignment="FULL",
        timeframe_confidence=100.0,
        timeframe_summary=(
            "Timeframes are aligned."
        ),

        market_session="LONDON",
        session_activity="HIGH",
        session_condition="FAVORABLE",
        session_summary=(
            "London session is active."
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

    assert result["decision"].approved is False

    assert (
        "risk_level"
        in result["decision"].gates_failed
    )

    assert "trade_plan" not in result

    assert "risk_gate" not in result

    assert "approval" not in result


def test_ai_trade_setup_rejects_low_risk_reward(
    monkeypatch,
):
    """
    Test that a bullish decision can still be rejected
    later when the planned risk/reward ratio is below 2.
    """

    install_bullish_low_risk_intelligence(
        monkeypatch,
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
        take_profit=1.1075,
        account_balance=10000,
        risk_percent=1,
        trade_risk_amount=100,
        lot_size=0.10,
    )

    assert result["decision"].action == "BUY"

    assert (
        result["trade_plan"].risk_reward
        == 1.5
    )

    assert (
        result["risk_validation"].approved
        is False
    )

    assert (
        result["approval"].approved
        is False
    )

    assert "reasoning" in result