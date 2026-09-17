"""
Tests for app.services.trade_setup_service.TradeSetupService.

These tests validate the deterministic trade-setup engine independently
from FastAPI, MT5, and the frontend.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.services.trade_setup_service import TradeSetupService


# ============================================================
# TEST DATA
# ============================================================


@dataclass
class FakeCandle:
    close_price: float


def candles(
    close: float = 1.1000,
) -> list[FakeCandle]:
    """
    TradeSetupService currently requires only the latest close price,
    so one deterministic candle is sufficient for these unit tests.
    """
    return [
        FakeCandle(
            close_price=close,
        )
    ]


def bullish_bias(
    *,
    confidence: float = 60.0,
    score: float = 7.5,
    strength: str = "STRONG",
) -> dict:
    return {
        "bias": "BULLISH",
        "strength": strength,
        "confidence": confidence,
        "score": score,
        "bullish_score": 10.0,
        "bearish_score": 2.5,
        "reasons": [],
    }


def bearish_bias(
    *,
    confidence: float = 60.0,
    score: float = -7.5,
    strength: str = "STRONG",
) -> dict:
    return {
        "bias": "BEARISH",
        "strength": strength,
        "confidence": confidence,
        "score": score,
        "bullish_score": 2.5,
        "bearish_score": 10.0,
        "reasons": [],
    }


def neutral_bias() -> dict:
    return {
        "bias": "NEUTRAL",
        "strength": "VERY_WEAK",
        "confidence": 0.0,
        "score": 0.0,
        "bullish_score": 4.0,
        "bearish_score": 4.0,
        "reasons": [],
    }


def bullish_order_block(
    *,
    low: float = 1.0995,
    high: float = 1.1005,
) -> dict:
    return {
        "type": "ORDER_BLOCK_BULLISH",
        "low_price": low,
        "high_price": high,
    }


def bearish_order_block(
    *,
    low: float = 1.0995,
    high: float = 1.1005,
) -> dict:
    return {
        "type": "ORDER_BLOCK_BEARISH",
        "low_price": low,
        "high_price": high,
    }


def bullish_fvg(
    *,
    low: float = 1.0995,
    high: float = 1.1005,
) -> dict:
    return {
        "type": "FVG_BULLISH",
        "lower_price": low,
        "upper_price": high,
    }


def bearish_fvg(
    *,
    low: float = 1.0995,
    high: float = 1.1005,
) -> dict:
    return {
        "type": "FVG_BEARISH",
        "lower_price": low,
        "upper_price": high,
    }


def support_resistance() -> dict:
    return {
        "support_zones": [
            {
                "type": "SUPPORT",
                "lower_price": 1.0995,
                "upper_price": 1.1005,
                "center_price": 1.1000,
                "touch_count": 3,
            },
            {
                "type": "SUPPORT",
                "lower_price": 1.0945,
                "upper_price": 1.0955,
                "center_price": 1.0950,
                "touch_count": 2,
            },
        ],
        "resistance_zones": [
            {
                "type": "RESISTANCE",
                "lower_price": 1.1035,
                "upper_price": 1.1045,
                "center_price": 1.1040,
                "touch_count": 3,
            },
            {
                "type": "RESISTANCE",
                "lower_price": 1.1095,
                "upper_price": 1.1105,
                "center_price": 1.1100,
                "touch_count": 2,
            },
        ],
    }


def premium_discount() -> dict:
    return {
        "range_low": 1.0950,
        "range_high": 1.1050,
        "equilibrium": 1.1000,
        "discount_low": 1.0950,
        "discount_high": 1.1000,
        "premium_low": 1.1000,
        "premium_high": 1.1050,
    }


def analyze(
    *,
    close: float = 1.1000,
    bias: dict | None = None,
    atr: float | None = 0.0020,
    bos: dict | None = None,
    choch: dict | None = None,
    sweep: dict | None = None,
    order_block: dict | None = None,
    fvg: dict | None = None,
    premium_discount_data: dict | None = None,
    sr: dict | None = None,
    symbol: str = "EURUSD",
    timeframe: str = "H1",
) -> dict:
    return TradeSetupService.analyze(
        candles=candles(
            close,
        ),
        market_bias=bias,
        atr=atr,
        latest_bos=bos,
        latest_choch=choch,
        latest_liquidity_sweep=sweep,
        latest_order_block=order_block,
        latest_fvg=fvg,
        latest_premium_discount=premium_discount_data,
        support_resistance=sr,
        symbol=symbol,
        timeframe=timeframe,
    )


# ============================================================
# INPUT VALIDATION
# ============================================================


def test_trade_setup_rejects_empty_candles():
    with pytest.raises(
        ValueError,
        match="requires candle data",
    ):
        TradeSetupService.analyze(
            candles=[],
            market_bias=bullish_bias(),
            atr=0.0020,
        )


def test_trade_setup_rejects_invalid_latest_close():
    with pytest.raises(
        ValueError,
        match="valid close price",
    ):
        TradeSetupService.analyze(
            candles=[
                {
                    "close": None,
                }
            ],
            market_bias=bullish_bias(),
            atr=0.0020,
        )


@pytest.mark.parametrize(
    "atr",
    [
        None,
        0.0,
        -0.0010,
        "bad-atr",
    ],
)
def test_missing_or_invalid_atr_returns_wait(
    atr,
):
    result = analyze(
        bias=bullish_bias(),
        atr=atr,
        order_block=bullish_order_block(),
    )

    assert result["status"] == "WAIT"
    assert result["engine"] == "DETERMINISTIC"

    assert any(
        "ATR" in reason
        for reason in result["reasons"]
    )


# ============================================================
# MARKET BIAS FILTER
# ============================================================


def test_neutral_bias_returns_wait():
    result = analyze(
        bias=neutral_bias(),
        order_block=bullish_order_block(),
    )

    assert result["status"] == "WAIT"
    assert result["direction"] is None
    assert result["bias"] == "NEUTRAL"

    assert any(
        "neutral" in reason.lower()
        for reason in result["reasons"]
    )


def test_missing_market_bias_returns_wait():
    result = analyze(
        bias=None,
        order_block=bullish_order_block(),
    )

    assert result["status"] == "WAIT"
    assert result["direction"] is None
    assert result["bias"] is None


def test_invalid_market_bias_returns_wait():
    result = analyze(
        bias={
            "bias": "SIDEWAYS",
            "confidence": 50.0,
            "score": 0.0,
        },
        order_block=bullish_order_block(),
    )

    assert result["status"] == "WAIT"
    assert result["direction"] is None


def test_bullish_bias_maps_to_buy_direction():
    result = analyze(
        bias=bullish_bias(),
        order_block=bullish_order_block(),
    )

    assert result["direction"] == "BUY"


def test_bearish_bias_maps_to_sell_direction():
    result = analyze(
        bias=bearish_bias(),
        order_block=bearish_order_block(),
    )

    assert result["direction"] == "SELL"


# ============================================================
# STRUCTURE CONFLICT
# ============================================================


def test_bearish_choch_blocks_bullish_trade():
    result = analyze(
        bias=bullish_bias(),
        choch={
            "type": "CHOCH_BEARISH",
        },
        order_block=bullish_order_block(),
    )

    assert result["status"] == "WAIT"
    assert result["direction"] == "BUY"

    assert any(
        "CHoCH" in reason
        and "conflicts" in reason
        for reason in result["reasons"]
    )


def test_bullish_choch_blocks_bearish_trade():
    result = analyze(
        bias=bearish_bias(),
        choch={
            "type": "CHOCH_BULLISH",
        },
        order_block=bearish_order_block(),
    )

    assert result["status"] == "WAIT"
    assert result["direction"] == "SELL"


def test_bearish_bos_blocks_bullish_trade():
    result = analyze(
        bias=bullish_bias(),
        bos={
            "type": "BOS_BEARISH",
        },
        order_block=bullish_order_block(),
    )

    assert result["status"] == "WAIT"
    assert result["direction"] == "BUY"


def test_bullish_bos_blocks_bearish_trade():
    result = analyze(
        bias=bearish_bias(),
        bos={
            "type": "BOS_BULLISH",
        },
        order_block=bearish_order_block(),
    )

    assert result["status"] == "WAIT"
    assert result["direction"] == "SELL"


def test_matching_choch_can_restore_alignment_after_opposite_bos():
    result = analyze(
        bias=bullish_bias(),
        bos={
            "type": "BOS_BEARISH",
        },
        choch={
            "type": "CHOCH_BULLISH",
        },
        order_block=bullish_order_block(),
    )

    assert result["status"] == "TRADE"
    assert result["direction"] == "BUY"


# ============================================================
# DIRECTIONAL CONFIRMATIONS
# ============================================================


def test_bullish_bos_reason_is_returned():
    result = analyze(
        bias=bullish_bias(),
        bos={
            "type": "BOS_BULLISH",
        },
        order_block=bullish_order_block(),
    )

    assert any(
        "BOS confirms bullish" in reason
        for reason in result["reasons"]
    )


def test_bearish_bos_reason_is_returned():
    result = analyze(
        bias=bearish_bias(),
        bos={
            "type": "BOS_BEARISH",
        },
        order_block=bearish_order_block(),
    )

    assert any(
        "BOS confirms bearish" in reason
        for reason in result["reasons"]
    )


def test_low_side_liquidity_sweep_supports_buy():
    result = analyze(
        bias=bullish_bias(),
        sweep={
            "type": "LIQUIDITY_SWEEP_LOW",
            "level_price": 1.0990,
        },
        order_block=bullish_order_block(),
    )

    assert result["status"] == "TRADE"

    assert any(
        "Low-side liquidity sweep" in reason
        for reason in result["reasons"]
    )


def test_high_side_liquidity_sweep_supports_sell():
    result = analyze(
        bias=bearish_bias(),
        sweep={
            "type": "LIQUIDITY_SWEEP_HIGH",
            "level_price": 1.1010,
        },
        order_block=bearish_order_block(),
    )

    assert result["status"] == "TRADE"

    assert any(
        "High-side liquidity sweep" in reason
        for reason in result["reasons"]
    )


# ============================================================
# ENTRY SOURCES
# ============================================================


def test_bullish_order_block_creates_buy_entry():
    result = analyze(
        bias=bullish_bias(),
        order_block=bullish_order_block(),
    )

    assert result["status"] == "TRADE"
    assert result["direction"] == "BUY"
    assert result["entry"] is not None
    assert result["entry"]["source"] == "ORDER_BLOCK"


def test_bearish_order_block_creates_sell_entry():
    result = analyze(
        bias=bearish_bias(),
        order_block=bearish_order_block(),
    )

    assert result["status"] == "TRADE"
    assert result["direction"] == "SELL"
    assert result["entry"]["source"] == "ORDER_BLOCK"


def test_bullish_fvg_creates_buy_entry():
    result = analyze(
        bias=bullish_bias(),
        fvg=bullish_fvg(),
    )

    assert result["status"] == "TRADE"
    assert result["direction"] == "BUY"
    assert result["entry"]["source"] == "FVG"


def test_bearish_fvg_creates_sell_entry():
    result = analyze(
        bias=bearish_bias(),
        fvg=bearish_fvg(),
    )

    assert result["status"] == "TRADE"
    assert result["direction"] == "SELL"
    assert result["entry"]["source"] == "FVG"


def test_support_zone_can_create_buy_entry():
    result = analyze(
        bias=bullish_bias(),
        sr=support_resistance(),
    )

    assert result["status"] == "TRADE"
    assert result["direction"] == "BUY"
    assert result["entry"]["source"] == "SUPPORT"


def test_resistance_zone_can_create_sell_entry():
    result = analyze(
        close=1.1040,
        bias=bearish_bias(),
        sr=support_resistance(),
    )

    assert result["status"] == "TRADE"
    assert result["direction"] == "SELL"
    assert result["entry"]["source"] == "RESISTANCE"


def test_discount_zone_can_create_buy_entry():
    result = analyze(
        close=1.0995,
        bias=bullish_bias(),
        premium_discount_data=premium_discount(),
    )

    assert result["status"] == "TRADE"
    assert result["direction"] == "BUY"
    assert result["entry"]["source"] == "DISCOUNT"


def test_premium_zone_can_create_sell_entry():
    result = analyze(
        close=1.1005,
        bias=bearish_bias(),
        premium_discount_data=premium_discount(),
    )

    assert result["status"] == "TRADE"
    assert result["direction"] == "SELL"
    assert result["entry"]["source"] == "PREMIUM"


def test_order_block_has_priority_when_distance_is_equal():
    result = analyze(
        bias=bullish_bias(),
        order_block=bullish_order_block(),
        fvg=bullish_fvg(),
        sr=support_resistance(),
    )

    assert result["status"] == "TRADE"
    assert result["entry"]["source"] == "ORDER_BLOCK"


# ============================================================
# ENTRY DISTANCE FILTER
# ============================================================


def test_price_too_far_from_entry_zone_returns_wait():
    result = analyze(
        close=1.1020,
        bias=bullish_bias(),
        atr=0.0020,
        order_block=bullish_order_block(
            low=1.0995,
            high=1.1005,
        ),
    )

    assert result["status"] == "WAIT"
    assert result["direction"] == "BUY"
    assert result["entry"] is not None

    assert any(
        "too far" in reason.lower()
        for reason in result["reasons"]
    )


def test_price_inside_entry_zone_has_zero_distance():
    distance = (
        TradeSetupService._distance_to_zone(
            1.1000,
            1.0995,
            1.1005,
        )
    )

    assert distance == pytest.approx(
        0.0
    )


def test_distance_above_zone_is_calculated_correctly():
    distance = (
        TradeSetupService._distance_to_zone(
            1.1020,
            1.0995,
            1.1005,
        )
    )

    assert distance == pytest.approx(
        0.0015
    )


def test_distance_below_zone_is_calculated_correctly():
    distance = (
        TradeSetupService._distance_to_zone(
            1.0980,
            1.0995,
            1.1005,
        )
    )

    assert distance == pytest.approx(
        0.0015
    )


# ============================================================
# STOP LOSS
# ============================================================


def test_buy_stop_loss_is_below_entry():
    result = analyze(
        bias=bullish_bias(),
        order_block=bullish_order_block(),
    )

    assert result["status"] == "TRADE"

    assert (
        result["stop_loss"]
        < result["entry"]["preferred"]
    )


def test_sell_stop_loss_is_above_entry():
    result = analyze(
        bias=bearish_bias(),
        order_block=bearish_order_block(),
    )

    assert result["status"] == "TRADE"

    assert (
        result["stop_loss"]
        > result["entry"]["preferred"]
    )


def test_buy_liquidity_sweep_can_extend_stop_boundary():
    result = analyze(
        bias=bullish_bias(),
        order_block=bullish_order_block(),
        sweep={
            "type": "LIQUIDITY_SWEEP_LOW",
            "level_price": 1.0980,
        },
    )

    assert result["status"] == "TRADE"

    # ATR = 0.0020
    # buffer = 0.25 ATR = 0.0005
    # structural low = 1.0980
    # expected SL = 1.0975
    assert result["stop_loss"] == pytest.approx(
        1.0975
    )


def test_sell_liquidity_sweep_can_extend_stop_boundary():
    result = analyze(
        bias=bearish_bias(),
        order_block=bearish_order_block(),
        sweep={
            "type": "LIQUIDITY_SWEEP_HIGH",
            "level_price": 1.1020,
        },
    )

    assert result["status"] == "TRADE"

    assert result["stop_loss"] == pytest.approx(
        1.1025
    )


# ============================================================
# TARGETS AND RISK / REWARD
# ============================================================


def test_buy_targets_are_above_entry():
    result = analyze(
        bias=bullish_bias(),
        order_block=bullish_order_block(),
    )

    assert result["status"] == "TRADE"

    preferred = result["entry"][
        "preferred"
    ]

    assert all(
        target["price"] > preferred
        for target in result["targets"]
    )


def test_sell_targets_are_below_entry():
    result = analyze(
        bias=bearish_bias(),
        order_block=bearish_order_block(),
    )

    assert result["status"] == "TRADE"

    preferred = result["entry"][
        "preferred"
    ]

    assert all(
        target["price"] < preferred
        for target in result["targets"]
    )


def test_default_trade_contains_one_and_two_r_targets():
    result = analyze(
        bias=bullish_bias(),
        order_block=bullish_order_block(),
    )

    assert result["status"] == "TRADE"

    r_multiples = {
        target["rr"]
        for target in result["targets"]
        if target["source"]
        == "R_MULTIPLE"
    }

    assert 1.0 in r_multiples
    assert 2.0 in r_multiples


def test_valid_trade_satisfies_minimum_risk_reward():
    result = analyze(
        bias=bullish_bias(),
        order_block=bullish_order_block(),
    )

    assert result["status"] == "TRADE"

    assert (
        result["risk_reward"]
        >= TradeSetupService.MIN_RISK_REWARD
    )


def test_buy_can_add_resistance_structural_target():
    result = analyze(
        bias=bullish_bias(),
        order_block=bullish_order_block(),
        sr=support_resistance(),
    )

    assert result["status"] == "TRADE"

    structural_targets = [
        target
        for target in result["targets"]
        if target["name"]
        == "STRUCTURE"
    ]

    assert structural_targets

    assert (
        structural_targets[0]["source"]
        == "RESISTANCE"
    )


def test_sell_can_add_support_structural_target():
    result = analyze(
        bias=bearish_bias(),
        order_block=bearish_order_block(),
        sr=support_resistance(),
    )

    assert result["status"] == "TRADE"

    structural_targets = [
        target
        for target in result["targets"]
        if target["name"]
        == "STRUCTURE"
    ]

    assert structural_targets

    assert (
        structural_targets[0]["source"]
        == "SUPPORT"
    )


# ============================================================
# RESULT CONTRACT
# ============================================================


def test_trade_result_contains_expected_fields():
    result = analyze(
        bias=bullish_bias(),
        order_block=bullish_order_block(),
    )

    assert result["status"] == "TRADE"

    expected_fields = {
        "status",
        "direction",
        "symbol",
        "timeframe",
        "current_price",
        "entry",
        "stop_loss",
        "targets",
        "risk_reward",
        "bias",
        "bias_strength",
        "confidence",
        "bias_score",
        "reasons",
        "invalidation",
        "engine",
    }

    assert expected_fields.issubset(
        result.keys()
    )


def test_wait_result_contains_expected_fields():
    result = analyze(
        bias=neutral_bias(),
    )

    assert result["status"] == "WAIT"

    expected_fields = {
        "status",
        "direction",
        "symbol",
        "timeframe",
        "current_price",
        "entry",
        "stop_loss",
        "targets",
        "risk_reward",
        "bias",
        "bias_strength",
        "confidence",
        "bias_score",
        "reasons",
        "invalidation",
        "engine",
    }

    assert expected_fields.issubset(
        result.keys()
    )


def test_trade_result_preserves_symbol_and_timeframe():
    result = analyze(
        bias=bullish_bias(),
        order_block=bullish_order_block(),
        symbol="EURUSD",
        timeframe="H1",
    )

    assert result["symbol"] == "EURUSD"
    assert result["timeframe"] == "H1"


def test_trade_result_preserves_market_bias_information():
    result = analyze(
        bias=bullish_bias(
            confidence=60.0,
            score=7.5,
            strength="STRONG",
        ),
        order_block=bullish_order_block(),
    )

    assert result["bias"] == "BULLISH"
    assert result["bias_strength"] == "STRONG"

    assert result["confidence"] == pytest.approx(
        60.0
    )

    assert result["bias_score"] == pytest.approx(
        7.5
    )


def test_trade_engine_is_deterministic():
    result = analyze(
        bias=bullish_bias(),
        order_block=bullish_order_block(),
    )

    assert result["engine"] == "DETERMINISTIC"


def test_trade_result_contains_explanation_reasons():
    result = analyze(
        bias=bullish_bias(),
        bos={
            "type": "BOS_BULLISH",
        },
        order_block=bullish_order_block(),
    )

    assert result["reasons"]
    assert isinstance(
        result["reasons"],
        list,
    )

    assert all(
        isinstance(
            reason,
            str,
        )
        for reason in result["reasons"]
    )


def test_buy_result_contains_bullish_invalidation():
    result = analyze(
        bias=bullish_bias(),
        order_block=bullish_order_block(),
    )

    assert result["status"] == "TRADE"
    assert result["invalidation"] is not None

    assert "below" in (
        result["invalidation"]
        .lower()
    )


def test_sell_result_contains_bearish_invalidation():
    result = analyze(
        bias=bearish_bias(),
        order_block=bearish_order_block(),
    )

    assert result["status"] == "TRADE"
    assert result["invalidation"] is not None

    assert "above" in (
        result["invalidation"]
        .lower()
    )


# ============================================================
# HELPER BEHAVIOUR
# ============================================================


@pytest.mark.parametrize(
    (
        "first",
        "second",
        "expected",
    ),
    [
        (
            1.1000,
            1.1010,
            (
                1.1000,
                1.1010,
            ),
        ),
        (
            1.1010,
            1.1000,
            (
                1.1000,
                1.1010,
            ),
        ),
    ],
)
def test_normalise_zone_orders_prices(
    first,
    second,
    expected,
):
    result = (
        TradeSetupService
        ._normalise_zone(
            first,
            second,
        )
    )

    assert result == pytest.approx(
        expected
    )


def test_normalise_zone_rejects_equal_prices():
    result = (
        TradeSetupService
        ._normalise_zone(
            1.1000,
            1.1000,
        )
    )

    assert result is None


@pytest.mark.parametrize(
    "value",
    [
        None,
        True,
        False,
        "bad",
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_safe_float_rejects_invalid_values(
    value,
):
    assert (
        TradeSetupService
        ._safe_float(
            value
        )
        is None
    )


@pytest.mark.parametrize(
    (
        "value",
        "expected",
    ),
    [
        (
            "1.1005",
            1.1005,
        ),
        (
            1,
            1.0,
        ),
        (
            1.25,
            1.25,
        ),
    ],
)
def test_safe_float_accepts_numeric_values(
    value,
    expected,
):
    assert (
        TradeSetupService
        ._safe_float(
            value
        )
        == pytest.approx(
            expected
        )
    )


def test_deduplicate_preserves_reason_order():
    result = (
        TradeSetupService
        ._deduplicate(
            [
                "First",
                "Second",
                "First",
                "Third",
                "Second",
            ]
        )
    )

    assert result == [
        "First",
        "Second",
        "Third",
    ]