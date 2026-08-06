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
    """
    Test bullish market intelligence.

    Technical analysis and market structure
    have higher importance than news analysis.
    """

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

    # Weighted confidence:
    # Technical = 85 * 0.40
    # Structure = 85 * 0.40
    # News = 80 * 0.20
    # Total = 84.0
    assert result.confidence == 84.0


def test_bearish_market_intelligence():
    """
    Test bearish market intelligence.

    All three intelligence sources support
    a bearish market direction.
    """

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

    # Weighted confidence:
    # Technical = 75 * 0.40
    # Structure = 75 * 0.40
    # News = 70 * 0.20
    # Total = 74.0
    assert result.confidence == 74.0