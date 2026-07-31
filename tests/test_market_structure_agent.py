"""
test_market_structure_agent.py

Tests Market Structure Agent.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.intelligence.market_structure_agent import (
    MarketStructureAgent,
)


def test_bullish_bos_with_liquidity_and_fvg():

    result = MarketStructureAgent.analyze(
        price_structure="BOS_BULLISH",
        liquidity_sweep=True,
        order_block="BULLISH",
        fair_value_gap=True,
    )

    assert result.structure == "BOS"

    assert result.trend_direction == "BULLISH"

    assert result.liquidity_status == "SWEEP_COMPLETED"

    assert result.order_block == "BULLISH"

    assert result.fair_value_gap is True

    assert result.confidence > 70

    assert len(result.signals) > 0


def test_bearish_bos():

    result = MarketStructureAgent.analyze(
        price_structure="BOS_BEARISH",
        liquidity_sweep=False,
        order_block="BEARISH",
        fair_value_gap=False,
    )

    assert result.structure == "BOS"

    assert result.trend_direction == "BEARISH"

    assert result.order_block == "BEARISH"


def test_change_of_character():

    result = MarketStructureAgent.analyze(
        price_structure="CHOCH",
        liquidity_sweep=True,
        order_block="BULLISH",
        fair_value_gap=True,
    )

    assert result.structure == "CHoCH"

    assert result.trend_direction == "REVERSAL"
