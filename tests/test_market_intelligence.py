"""
test_market_intelligence.py

Tests Market Intelligence Agent.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.intelligence.market_intelligence import (
    MarketIntelligenceAgent,
)


from app.intelligence.technical_result import (
    TechnicalAnalysisResult,
)


from app.intelligence.news_result import (
    NewsAnalysisResult,
)


from app.intelligence.market_structure_result import (
    MarketStructureResult,
)


def test_bullish_market_intelligence():

    technical = TechnicalAnalysisResult(
        trend="BULLISH",
        momentum="STRONG",
        volatility="NORMAL",
        confidence=85,
        signals=["EMA confirms bullish trend"],
    )

    news = NewsAnalysisResult(
        currency="USD",
        impact="HIGH",
        sentiment="BULLISH",
        market_effect="USD strength expected",
        confidence=80,
    )

    structure = MarketStructureResult(
        structure="BOS",
        trend_direction="BULLISH",
        liquidity_status="SWEEP_COMPLETED",
        order_block="BULLISH",
        fair_value_gap=True,
        confidence=85,
        signals=["Bullish BOS detected"],
    )

    result = MarketIntelligenceAgent.analyze(
        technical_result=technical,
        news_result=news,
        structure_result=structure,
    )

    assert result.market_bias == "BULLISH"

    assert result.recommendation == "Consider BUY opportunities"

    assert result.risk_level == "LOW"

    assert result.confidence == 83.33


def test_bearish_market_intelligence():

    technical = TechnicalAnalysisResult(
        trend="BEARISH",
        momentum="WEAK",
        volatility="NORMAL",
        confidence=75,
        signals=[],
    )

    news = NewsAnalysisResult(
        currency="EUR",
        impact="HIGH",
        sentiment="BEARISH",
        market_effect="EUR weakness expected",
        confidence=70,
    )

    structure = MarketStructureResult(
        structure="BOS",
        trend_direction="BEARISH",
        liquidity_status="NO_SWEEP",
        order_block="BEARISH",
        fair_value_gap=False,
        confidence=75,
        signals=["Bearish BOS detected"],
    )

    result = MarketIntelligenceAgent.analyze(
        technical_result=technical,
        news_result=news,
        structure_result=structure,
    )

    assert result.market_bias == "BEARISH"

    assert result.recommendation == "Consider SELL opportunities"

    assert result.risk_level == "MEDIUM"

    assert result.confidence == 73.33
