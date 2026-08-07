"""
test_market_session_agent.py

Tests Forex market session intelligence.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.intelligence.market_session_agent import (
    MarketSessionAgent,
)


def test_london_market_session():
    """
    Test London Forex session detection.
    """

    result = MarketSessionAgent.analyze(
        hour_utc=9,
    )

    assert result.session == "LONDON"

    assert result.activity_level == "HIGH"

    assert result.trading_condition == "FAVORABLE"

    assert result.summary == (
        "London session is active with "
        "high market activity."
    )


def test_new_york_market_session():
    """
    Test New York Forex session detection.
    """

    result = MarketSessionAgent.analyze(
        hour_utc=17,
    )

    assert result.session == "NEW_YORK"

    assert result.activity_level == "HIGH"

    assert result.trading_condition == "FAVORABLE"

    assert result.summary == (
        "New York session is active with "
        "high market activity."
    )


def test_asian_market_session():
    """
    Test Asian Forex session detection.
    """

    result = MarketSessionAgent.analyze(
        hour_utc=3,
    )

    assert result.session == "ASIAN"

    assert result.activity_level == "MEDIUM"

    assert result.trading_condition == "NORMAL"

    assert result.summary == (
        "Asian session is active with "
        "moderate market activity."
    )


def test_london_new_york_overlap():
    """
    Test London and New York
    Forex session overlap.
    """

    result = MarketSessionAgent.analyze(
        hour_utc=14,
    )

    assert result.session == "LONDON_NEW_YORK_OVERLAP"

    assert result.activity_level == "VERY_HIGH"

    assert result.trading_condition == "HIGH_OPPORTUNITY"

    assert result.summary == (
        "London and New York sessions overlap "
        "with very high market activity."
    )

import pytest


def test_invalid_market_session_hour():
    """
    Test that invalid UTC hours are rejected.
    """

    with pytest.raises(ValueError):
        MarketSessionAgent.analyze(
            hour_utc=25,
        )