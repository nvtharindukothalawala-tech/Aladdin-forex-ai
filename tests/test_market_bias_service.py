from dataclasses import dataclass
from datetime import datetime

import pytest

from app.services.market_bias_service import (
    MarketBiasService,
)


@dataclass
class FakeCandle:
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    timestamp: datetime


def candle(
    close_price=1.1000,
):
    return FakeCandle(
        open_price=close_price - 0.0010,
        high_price=close_price + 0.0020,
        low_price=close_price - 0.0020,
        close_price=close_price,
        timestamp=datetime(
            2026,
            9,
            17,
            10,
            0,
        ),
    )


def indicator(
    value,
):
    return [
        {
            "time": 1,
            "value": value,
        }
    ]


def analyze(
    *,
    close=1.1000,
    ema=1.1000,
    rsi=50.0,
    adx=10.0,
    bos=None,
    choch=None,
    liquidity=None,
    order_block=None,
    fvg=None,
    engulfing=None,
    displacement=None,
    premium_discount=None,
):
    return MarketBiasService.analyze(
        candles=[
            candle(close),
        ],
        ema20_series=indicator(ema),
        rsi14_series=indicator(rsi),
        adx14_series=indicator(adx),
        latest_bos=bos,
        latest_choch=choch,
        latest_liquidity_sweep=liquidity,
        latest_order_block=order_block,
        latest_fvg=fvg,
        latest_engulfing=engulfing,
        latest_displacement=displacement,
        latest_premium_discount=premium_discount,
    )


def test_market_bias_rejects_empty_candles():

    with pytest.raises(
        ValueError,
        match="requires candle data",
    ):

        MarketBiasService.analyze(
            candles=[],
            ema20_series=[],
            rsi14_series=[],
            adx14_series=[],
        )


def test_bullish_ema_contributes_bullish_score():

    result = analyze(
        close=1.1100,
        ema=1.1000,
    )

    assert result["bullish_score"] == 2.0
    assert result["bearish_score"] == 0.0
    assert result["bias"] == "BULLISH"


def test_bearish_ema_contributes_bearish_score():

    result = analyze(
        close=1.0900,
        ema=1.1000,
    )

    assert result["bullish_score"] == 0.0
    assert result["bearish_score"] == 2.0
    assert result["bias"] == "BEARISH"


def test_rsi_above_50_is_bullish():

    result = analyze(
        close=1.1000,
        ema=1.1000,
        rsi=60.0,
    )

    assert result["bullish_score"] == 1.0


def test_rsi_below_50_is_bearish():

    result = analyze(
        close=1.1000,
        ema=1.1000,
        rsi=40.0,
    )

    assert result["bearish_score"] == 1.0


def test_adx_does_not_create_direction_by_itself():

    result = analyze(
        close=1.1000,
        ema=1.1000,
        rsi=50.0,
        adx=40.0,
    )

    assert result["bullish_score"] == 0.0
    assert result["bearish_score"] == 0.0
    assert result["bias"] == "NEUTRAL"


def test_adx_strengthens_bullish_ema_direction():

    result = analyze(
        close=1.1100,
        ema=1.1000,
        rsi=50.0,
        adx=30.0,
    )

    assert result["bullish_score"] == 2.5


def test_adx_strengthens_bearish_ema_direction():

    result = analyze(
        close=1.0900,
        ema=1.1000,
        rsi=50.0,
        adx=30.0,
    )

    assert result["bearish_score"] == 2.5


def test_bullish_bos_creates_bullish_bias():

    result = analyze(
        bos={
            "type": "BOS_BULLISH",
        },
    )

    assert result["bullish_score"] == 3.0
    assert result["bias"] == "BULLISH"


def test_bearish_bos_creates_bearish_bias():

    result = analyze(
        bos={
            "type": "BOS_BEARISH",
        },
    )

    assert result["bearish_score"] == 3.0
    assert result["bias"] == "BEARISH"


def test_bullish_choch_contributes_bullish_score():

    result = analyze(
        choch={
            "type": "CHOCH_BULLISH",
        },
    )

    assert result["bullish_score"] == 3.0


def test_bearish_choch_contributes_bearish_score():

    result = analyze(
        choch={
            "type": "CHOCH_BEARISH",
        },
    )

    assert result["bearish_score"] == 3.0


def test_low_side_liquidity_sweep_is_bullish():

    result = analyze(
        liquidity={
            "type": "LIQUIDITY_SWEEP_LOW",
        },
    )

    assert result["bullish_score"] == 1.5


def test_high_side_liquidity_sweep_is_bearish():

    result = analyze(
        liquidity={
            "type": "LIQUIDITY_SWEEP_HIGH",
        },
    )

    assert result["bearish_score"] == 1.5


def test_bullish_order_block_adds_score():

    result = analyze(
        order_block={
            "type": "ORDER_BLOCK_BULLISH",
        },
    )

    assert result["bullish_score"] == 1.0


def test_bearish_order_block_adds_score():

    result = analyze(
        order_block={
            "type": "ORDER_BLOCK_BEARISH",
        },
    )

    assert result["bearish_score"] == 1.0


def test_bullish_fvg_adds_score():

    result = analyze(
        fvg={
            "type": "FVG_BULLISH",
        },
    )

    assert result["bullish_score"] == 1.0


def test_bearish_fvg_adds_score():

    result = analyze(
        fvg={
            "type": "FVG_BEARISH",
        },
    )

    assert result["bearish_score"] == 1.0


def test_bullish_engulfing_adds_score():

    result = analyze(
        engulfing={
            "type": "ENGULFING_BULLISH",
        },
    )

    assert result["bullish_score"] == 1.0


def test_bearish_engulfing_adds_score():

    result = analyze(
        engulfing={
            "type": "ENGULFING_BEARISH",
        },
    )

    assert result["bearish_score"] == 1.0


def test_bullish_displacement_adds_score():

    result = analyze(
        displacement={
            "type": "DISPLACEMENT_BULLISH",
        },
    )

    assert result["bullish_score"] == 1.5


def test_bearish_displacement_adds_score():

    result = analyze(
        displacement={
            "type": "DISPLACEMENT_BEARISH",
        },
    )

    assert result["bearish_score"] == 1.5


def test_discount_location_adds_small_bullish_score():

    result = analyze(
        close=1.1250,
        ema=1.1250,
        premium_discount={
            "range_low": 1.1000,
            "range_high": 1.2000,
            "equilibrium": 1.1500,
        },
    )

    assert result["bullish_score"] == 0.5


def test_premium_location_adds_small_bearish_score():

    result = analyze(
        close=1.1750,
        ema=1.1750,
        premium_discount={
            "range_low": 1.1000,
            "range_high": 1.2000,
            "equilibrium": 1.1500,
        },
    )

    assert result["bearish_score"] == 0.5


def test_conflicting_equal_bos_and_choch_is_neutral():

    result = analyze(
        bos={
            "type": "BOS_BULLISH",
        },
        choch={
            "type": "CHOCH_BEARISH",
        },
    )

    assert result["bullish_score"] == 3.0
    assert result["bearish_score"] == 3.0
    assert result["score"] == 0.0
    assert result["bias"] == "NEUTRAL"
    assert result["confidence"] == 0.0


def test_strong_combined_bullish_evidence():

    result = analyze(
        close=1.1200,
        ema=1.1000,
        rsi=62.0,
        adx=30.0,
        bos={
            "type": "BOS_BULLISH",
        },
        choch={
            "type": "CHOCH_BULLISH",
        },
        liquidity={
            "type": "LIQUIDITY_SWEEP_LOW",
        },
        order_block={
            "type": "ORDER_BLOCK_BULLISH",
        },
        fvg={
            "type": "FVG_BULLISH",
        },
        engulfing={
            "type": "ENGULFING_BULLISH",
        },
        displacement={
            "type": "DISPLACEMENT_BULLISH",
        },
    )

    assert result["bias"] == "BULLISH"
    assert result["score"] > 0
    assert result["confidence"] == 100.0
    assert result["bullish_score"] > 0
    assert result["bearish_score"] == 0


def test_strong_combined_bearish_evidence():

    result = analyze(
        close=1.0800,
        ema=1.1000,
        rsi=38.0,
        adx=30.0,
        bos={
            "type": "BOS_BEARISH",
        },
        choch={
            "type": "CHOCH_BEARISH",
        },
        liquidity={
            "type": "LIQUIDITY_SWEEP_HIGH",
        },
        order_block={
            "type": "ORDER_BLOCK_BEARISH",
        },
        fvg={
            "type": "FVG_BEARISH",
        },
        engulfing={
            "type": "ENGULFING_BEARISH",
        },
        displacement={
            "type": "DISPLACEMENT_BEARISH",
        },
    )

    assert result["bias"] == "BEARISH"
    assert result["score"] < 0
    assert result["confidence"] == 100.0
    assert result["bearish_score"] > 0
    assert result["bullish_score"] == 0


def test_result_contains_explanation_reasons():

    result = analyze(
        close=1.1100,
        ema=1.1000,
        rsi=60.0,
        bos={
            "type": "BOS_BULLISH",
        },
    )

    assert result["reasons"]

    sources = {
        reason["source"]
        for reason in result["reasons"]
    }

    assert "EMA20" in sources
    assert "RSI14" in sources
    assert "BOS" in sources


def test_missing_optional_evidence_is_safe():

    result = MarketBiasService.analyze(
        candles=[
            candle(1.1000),
        ],
        ema20_series=[],
        rsi14_series=[],
        adx14_series=[],
    )

    assert result["bias"] == "NEUTRAL"
    assert result["score"] == 0.0
    assert result["confidence"] == 0.0


def test_numeric_indicator_series_is_supported():

    result = MarketBiasService.analyze(
        candles=[
            candle(1.1100),
        ],
        ema20_series=[
            1.1000,
        ],
        rsi14_series=[
            60.0,
        ],
        adx14_series=[
            30.0,
        ],
    )

    assert result["bias"] == "BULLISH"
    assert result["ema20"] == 1.1000
    assert result["rsi14"] == 60.0
    assert result["adx14"] == 30.0