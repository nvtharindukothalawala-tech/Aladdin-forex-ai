"""
test_news_agent.py

Tests Forex News Analysis Agent.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.intelligence.news_agent import (
    NewsAgent,
)


def test_bullish_high_impact_news():

    result = NewsAgent.analyze(
        currency="USD",
        event_type="Interest Rate Decision",
        importance="HIGH",
        sentiment="BULLISH",
    )

    assert result.currency == "USD"

    assert result.impact == "HIGH"

    assert result.sentiment == "BULLISH"

    assert "strength" in result.market_effect

    assert result.confidence > 50


def test_bearish_medium_impact_news():

    result = NewsAgent.analyze(
        currency="EUR",
        event_type="Inflation Report",
        importance="MEDIUM",
        sentiment="BEARISH",
    )

    assert result.currency == "EUR"

    assert result.impact == "MEDIUM"

    assert result.sentiment == "BEARISH"

    assert "weakness" in result.market_effect
