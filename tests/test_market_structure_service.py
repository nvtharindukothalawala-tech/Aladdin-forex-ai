"""
test_market_structure_service.py

Deterministic tests for the candle-based
ALADDIN Market Structure Service.

These tests use local Candle objects only.
They do not connect to MetaTrader 5.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from datetime import datetime, timedelta

from app.market.candle import Candle
from app.services.market_structure_service import (
    MarketStructureService,
)


BASE_TIME = datetime(2026, 1, 1, 0, 0, 0)


def make_candle(
    index,
    open_price,
    high_price,
    low_price,
    close_price,
):
    """
    Create one deterministic H1 EURUSD candle.
    """

    return Candle(
        symbol="EURUSD",
        timeframe="H1",
        open_price=open_price,
        high_price=high_price,
        low_price=low_price,
        close_price=close_price,
        volume=100.0,
        timestamp=BASE_TIME + timedelta(hours=index),
    )


def test_find_swing_highs_detects_confirmed_swing():
    """
    A swing high must be higher than the highs
    on both sides of the candle.
    """

    candles = [
        make_candle(0, 1.1000, 1.1010, 1.0990, 1.1005),
        make_candle(1, 1.1005, 1.1020, 1.1000, 1.1010),
        make_candle(2, 1.1010, 1.1050, 1.1005, 1.1030),
        make_candle(3, 1.1030, 1.1025, 1.1000, 1.1010),
        make_candle(4, 1.1010, 1.1015, 1.0995, 1.1000),
    ]

    result = MarketStructureService.find_swing_highs(
        candles,
        lookback=2,
    )

    assert len(result) == 1
    assert result[0]["index"] == 2
    assert result[0]["price"] == 1.1050
    assert result[0]["timestamp"] == candles[2].timestamp


def test_find_swing_lows_detects_confirmed_swing():
    """
    A swing low must be lower than the lows
    on both sides of the candle.
    """

    candles = [
        make_candle(0, 1.1040, 1.1050, 1.1020, 1.1030),
        make_candle(1, 1.1030, 1.1040, 1.1010, 1.1020),
        make_candle(2, 1.1020, 1.1030, 1.0970, 1.0990),
        make_candle(3, 1.0990, 1.1035, 1.1000, 1.1020),
        make_candle(4, 1.1020, 1.1040, 1.1010, 1.1030),
    ]

    result = MarketStructureService.find_swing_lows(
        candles,
        lookback=2,
    )

    assert len(result) == 1
    assert result[0]["index"] == 2
    assert result[0]["price"] == 1.0970
    assert result[0]["timestamp"] == candles[2].timestamp


def test_detect_bullish_bos_after_swing_high():
    """
    A close above a confirmed swing high
    must produce a bullish BOS.
    """

    candles = [
        make_candle(0, 1.1000, 1.1010, 1.0990, 1.1005),
        make_candle(1, 1.1005, 1.1020, 1.1000, 1.1010),
        make_candle(2, 1.1010, 1.1050, 1.1005, 1.1030),
        make_candle(3, 1.1030, 1.1040, 1.1010, 1.1020),
        make_candle(4, 1.1020, 1.1045, 1.1010, 1.1040),
        make_candle(5, 1.1040, 1.1070, 1.1030, 1.1060),
    ]

    swing_highs = [
        {
            "index": 2,
            "price": 1.1050,
            "timestamp": candles[2].timestamp,
        }
    ]

    result = MarketStructureService.detect_bos(
        candles,
        swing_highs,
        [],
    )

    assert result is not None
    assert result["type"] == "BOS_BULLISH"
    assert result["broken_price"] == 1.1050
    assert result["swing_index"] == 2
    assert result["break_index"] == 5
    assert result["timestamp"] == candles[5].timestamp


def test_detect_bearish_bos_after_swing_low():
    """
    A close below a confirmed swing low
    must produce a bearish BOS.
    """

    candles = [
        make_candle(0, 1.1050, 1.1060, 1.1030, 1.1040),
        make_candle(1, 1.1040, 1.1050, 1.1020, 1.1030),
        make_candle(2, 1.1030, 1.1040, 1.0990, 1.1010),
        make_candle(3, 1.1010, 1.1030, 1.1000, 1.1020),
        make_candle(4, 1.1020, 1.1030, 1.0995, 1.1000),
        make_candle(5, 1.1000, 1.1010, 1.0970, 1.0980),
    ]

    swing_lows = [
        {
            "index": 2,
            "price": 1.0990,
            "timestamp": candles[2].timestamp,
        }
    ]

    result = MarketStructureService.detect_bos(
        candles,
        [],
        swing_lows,
    )

    assert result is not None
    assert result["type"] == "BOS_BEARISH"
    assert result["broken_price"] == 1.0990
    assert result["swing_index"] == 2
    assert result["break_index"] == 5
    assert result["timestamp"] == candles[5].timestamp


def test_detect_bos_returns_none_without_break():
    """
    No candle closing beyond the supplied swing
    levels must produce no BOS.
    """

    candles = [
        make_candle(0, 1.1000, 1.1010, 1.0990, 1.1000),
        make_candle(1, 1.1000, 1.1030, 1.0995, 1.1020),
        make_candle(2, 1.1020, 1.1040, 1.1000, 1.1030),
        make_candle(3, 1.1030, 1.1045, 1.1010, 1.1040),
    ]

    swing_highs = [
        {
            "index": 1,
            "price": 1.1050,
            "timestamp": candles[1].timestamp,
        }
    ]

    swing_lows = [
        {
            "index": 1,
            "price": 1.0980,
            "timestamp": candles[1].timestamp,
        }
    ]

    result = MarketStructureService.detect_bos(
        candles,
        swing_highs,
        swing_lows,
    )

    assert result is None


def test_detect_bearish_choch_after_bullish_bos():
    """
    After bullish BOS, a close below a later
    swing low must produce bearish CHoCH.
    """

    candles = [
        make_candle(0, 1.1000, 1.1010, 1.0990, 1.1000),
        make_candle(1, 1.1000, 1.1030, 1.0995, 1.1020),
        make_candle(2, 1.1020, 1.1060, 1.1010, 1.1055),
        make_candle(3, 1.1055, 1.1070, 1.1040, 1.1060),
        make_candle(4, 1.1060, 1.1065, 1.1020, 1.1030),
        make_candle(5, 1.1030, 1.1050, 1.1010, 1.1040),
        make_candle(6, 1.1040, 1.1045, 1.0990, 1.1000),
    ]

    latest_bos = {
        "type": "BOS_BULLISH",
        "broken_price": 1.1030,
        "swing_index": 1,
        "break_index": 2,
        "timestamp": candles[2].timestamp,
    }

    swing_lows = [
        {
            "index": 4,
            "price": 1.1020,
            "timestamp": candles[4].timestamp,
        }
    ]

    result = MarketStructureService.detect_choch(
        candles,
        [],
        swing_lows,
        latest_bos,
    )

    assert result is not None
    assert result["type"] == "CHOCH_BEARISH"
    assert result["broken_price"] == 1.1020
    assert result["swing_index"] == 4
    assert result["break_index"] == 6
    assert result["timestamp"] == candles[6].timestamp


def test_detect_bullish_choch_after_bearish_bos():
    """
    After bearish BOS, a close above a later
    swing high must produce bullish CHoCH.
    """

    candles = [
        make_candle(0, 1.1060, 1.1070, 1.1050, 1.1060),
        make_candle(1, 1.1060, 1.1065, 1.1020, 1.1030),
        make_candle(2, 1.1030, 1.1040, 1.0990, 1.1000),
        make_candle(3, 1.1000, 1.1020, 1.0980, 1.0990),
        make_candle(4, 1.0990, 1.1030, 1.0985, 1.1020),
        make_candle(5, 1.1020, 1.1025, 1.1000, 1.1010),
        make_candle(6, 1.1010, 1.1050, 1.1005, 1.1040),
    ]

    latest_bos = {
        "type": "BOS_BEARISH",
        "broken_price": 1.1020,
        "swing_index": 1,
        "break_index": 2,
        "timestamp": candles[2].timestamp,
    }

    swing_highs = [
        {
            "index": 4,
            "price": 1.1030,
            "timestamp": candles[4].timestamp,
        }
    ]

    result = MarketStructureService.detect_choch(
        candles,
        swing_highs,
        [],
        latest_bos,
    )

    assert result is not None
    assert result["type"] == "CHOCH_BULLISH"
    assert result["broken_price"] == 1.1030
    assert result["swing_index"] == 4
    assert result["break_index"] == 6
    assert result["timestamp"] == candles[6].timestamp


def test_detect_choch_returns_none_without_bos():
    """
    CHoCH detection requires an existing BOS.
    """

    candles = [
        make_candle(0, 1.1000, 1.1010, 1.0990, 1.1000),
        make_candle(1, 1.1000, 1.1020, 1.0995, 1.1010),
        make_candle(2, 1.1010, 1.1030, 1.1000, 1.1020),
    ]

    result = MarketStructureService.detect_choch(
        candles,
        [],
        [],
        None,
    )

    assert result is None


def test_detect_high_side_liquidity_sweep():
    """
    Price trading above a confirmed swing high
    and closing back below it must produce a
    high-side liquidity sweep.
    """

    candles = [
        make_candle(0, 1.1000, 1.1010, 1.0990, 1.1000),
        make_candle(1, 1.1000, 1.1050, 1.1000, 1.1030),
        make_candle(2, 1.1030, 1.1040, 1.1010, 1.1020),
        make_candle(3, 1.1020, 1.1060, 1.1010, 1.1040),
    ]

    swing_highs = [
        {
            "index": 1,
            "price": 1.1050,
            "timestamp": candles[1].timestamp,
        }
    ]

    result = MarketStructureService.detect_liquidity_sweep(
        candles,
        swing_highs,
        [],
    )

    assert result is not None
    assert result["type"] == "LIQUIDITY_SWEEP_HIGH"
    assert result["level_price"] == 1.1050
    assert result["swing_index"] == 1
    assert result["sweep_index"] == 3
    assert result["timestamp"] == candles[3].timestamp


def test_detect_low_side_liquidity_sweep():
    """
    Price trading below a confirmed swing low
    and closing back above it must produce a
    low-side liquidity sweep.
    """

    candles = [
        make_candle(0, 1.1050, 1.1060, 1.1030, 1.1040),
        make_candle(1, 1.1040, 1.1050, 1.0990, 1.1010),
        make_candle(2, 1.1010, 1.1030, 1.1000, 1.1020),
        make_candle(3, 1.1020, 1.1030, 1.0980, 1.1000),
    ]

    swing_lows = [
        {
            "index": 1,
            "price": 1.0990,
            "timestamp": candles[1].timestamp,
        }
    ]

    result = MarketStructureService.detect_liquidity_sweep(
        candles,
        [],
        swing_lows,
    )

    assert result is not None
    assert result["type"] == "LIQUIDITY_SWEEP_LOW"
    assert result["level_price"] == 1.0990
    assert result["swing_index"] == 1
    assert result["sweep_index"] == 3
    assert result["timestamp"] == candles[3].timestamp


def test_detect_liquidity_sweep_returns_none_without_sweep():
    """
    Price remaining inside the supplied swing
    levels must not produce a liquidity sweep.
    """

    candles = [
        make_candle(0, 1.1000, 1.1020, 1.0990, 1.1010),
        make_candle(1, 1.1010, 1.1050, 1.0980, 1.1020),
        make_candle(2, 1.1020, 1.1040, 1.0990, 1.1030),
        make_candle(3, 1.1030, 1.1045, 1.0985, 1.1020),
    ]

    swing_highs = [
        {
            "index": 1,
            "price": 1.1050,
            "timestamp": candles[1].timestamp,
        }
    ]

    swing_lows = [
        {
            "index": 1,
            "price": 1.0980,
            "timestamp": candles[1].timestamp,
        }
    ]

    result = MarketStructureService.detect_liquidity_sweep(
        candles,
        swing_highs,
        swing_lows,
    )

    assert result is None


def test_detect_liquidity_sweep_requires_strict_level_cross():
    """
    Touching a swing level exactly is not a sweep.

    The existing service requires the candle high
    to be strictly above a swing high or the candle
    low to be strictly below a swing low.
    """

    candles = [
        make_candle(0, 1.1000, 1.1020, 1.0990, 1.1010),
        make_candle(1, 1.1010, 1.1050, 1.0980, 1.1020),
        make_candle(2, 1.1020, 1.1050, 1.0980, 1.1010),
    ]

    swing_highs = [
        {
            "index": 1,
            "price": 1.1050,
            "timestamp": candles[1].timestamp,
        }
    ]

    swing_lows = [
        {
            "index": 1,
            "price": 1.0980,
            "timestamp": candles[1].timestamp,
        }
    ]

    result = MarketStructureService.detect_liquidity_sweep(
        candles,
        swing_highs,
        swing_lows,
    )

    assert result is None


def test_detect_bullish_order_block_uses_nearest_bearish_candle():
    """Bullish BOS selects the nearest previous bearish candle."""
    candles = [
        make_candle(0, 1.1000, 1.1020, 1.0990, 1.1010),
        make_candle(1, 1.1010, 1.1020, 1.0995, 1.1000),
        make_candle(2, 1.1000, 1.1030, 1.0995, 1.1020),
        make_candle(3, 1.1020, 1.1030, 1.1000, 1.1010),
        make_candle(4, 1.1010, 1.1060, 1.1005, 1.1050),
    ]
    latest_bos = {
        "type": "BOS_BULLISH",
        "broken_price": 1.1040,
        "swing_index": 2,
        "break_index": 4,
        "timestamp": candles[4].timestamp,
    }

    result = MarketStructureService.detect_order_block(candles, latest_bos)

    assert result is not None
    assert result["type"] == "ORDER_BLOCK_BULLISH"
    assert result["candle_index"] == 3
    assert result["high_price"] == candles[3].high_price
    assert result["low_price"] == candles[3].low_price
    assert result["open_price"] == candles[3].open_price
    assert result["close_price"] == candles[3].close_price
    assert result["timestamp"] == candles[3].timestamp


def test_detect_bearish_order_block_uses_nearest_bullish_candle():
    """Bearish BOS selects the nearest previous bullish candle."""
    candles = [
        make_candle(0, 1.1050, 1.1060, 1.1030, 1.1040),
        make_candle(1, 1.1040, 1.1060, 1.1035, 1.1050),
        make_candle(2, 1.1050, 1.1055, 1.1020, 1.1030),
        make_candle(3, 1.1030, 1.1050, 1.1025, 1.1040),
        make_candle(4, 1.1040, 1.1045, 1.0980, 1.0990),
    ]
    latest_bos = {
        "type": "BOS_BEARISH",
        "broken_price": 1.1000,
        "swing_index": 2,
        "break_index": 4,
        "timestamp": candles[4].timestamp,
    }

    result = MarketStructureService.detect_order_block(candles, latest_bos)

    assert result is not None
    assert result["type"] == "ORDER_BLOCK_BEARISH"
    assert result["candle_index"] == 3
    assert result["high_price"] == candles[3].high_price
    assert result["low_price"] == candles[3].low_price
    assert result["open_price"] == candles[3].open_price
    assert result["close_price"] == candles[3].close_price
    assert result["timestamp"] == candles[3].timestamp


def test_detect_order_block_returns_none_without_bos():
    """Order Block detection requires an existing BOS."""
    candles = [
        make_candle(0, 1.1000, 1.1020, 1.0990, 1.1010),
        make_candle(1, 1.1010, 1.1030, 1.1000, 1.1020),
    ]

    result = MarketStructureService.detect_order_block(candles, None)

    assert result is None


def test_detect_order_block_returns_none_without_opposite_candle():
    """No opposite candle before BOS means no Order Block."""
    candles = [
        make_candle(0, 1.1000, 1.1020, 1.0990, 1.1010),
        make_candle(1, 1.1010, 1.1030, 1.1000, 1.1020),
        make_candle(2, 1.1020, 1.1040, 1.1010, 1.1030),
        make_candle(3, 1.1030, 1.1060, 1.1020, 1.1050),
    ]
    latest_bos = {
        "type": "BOS_BULLISH",
        "broken_price": 1.1040,
        "swing_index": 2,
        "break_index": 3,
        "timestamp": candles[3].timestamp,
    }

    result = MarketStructureService.detect_order_block(candles, latest_bos)

    assert result is None

def test_detect_fvg_detects_bullish_gap():
    """Candle 3 low strictly above Candle 1 high creates bullish FVG."""
    candles = [
        make_candle(0, 1.1000, 1.1010, 1.0990, 1.1005),
        make_candle(1, 1.1005, 1.1040, 1.1000, 1.1030),
        make_candle(2, 1.1030, 1.1050, 1.1020, 1.1040),
    ]

    result = MarketStructureService.detect_fvg(candles)

    assert result is not None
    assert result["type"] == "FVG_BULLISH"
    assert result["start_index"] == 0
    assert result["middle_index"] == 1
    assert result["end_index"] == 2
    assert result["lower_price"] == candles[0].high_price
    assert result["upper_price"] == candles[2].low_price
    assert result["timestamp"] == candles[2].timestamp


def test_detect_fvg_detects_bearish_gap():
    """Candle 3 high strictly below Candle 1 low creates bearish FVG."""
    candles = [
        make_candle(0, 1.1050, 1.1060, 1.1040, 1.1050),
        make_candle(1, 1.1050, 1.1055, 1.1010, 1.1020),
        make_candle(2, 1.1020, 1.1030, 1.1000, 1.1010),
    ]

    result = MarketStructureService.detect_fvg(candles)

    assert result is not None
    assert result["type"] == "FVG_BEARISH"
    assert result["start_index"] == 0
    assert result["middle_index"] == 1
    assert result["end_index"] == 2
    assert result["lower_price"] == candles[2].high_price
    assert result["upper_price"] == candles[0].low_price
    assert result["timestamp"] == candles[2].timestamp


def test_detect_fvg_returns_latest_gap():
    """When several FVGs exist, the event with latest end_index is returned."""
    candles = [
        make_candle(0, 1.1000, 1.1010, 1.0990, 1.1000),
        make_candle(1, 1.1000, 1.1040, 1.1000, 1.1030),
        make_candle(2, 1.1030, 1.1050, 1.1020, 1.1040),
        make_candle(3, 1.1040, 1.1050, 1.1030, 1.1040),
        make_candle(4, 1.1040, 1.1050, 1.1030, 1.1040),
        make_candle(5, 1.1040, 1.1045, 1.1000, 1.1010),
        make_candle(6, 1.1010, 1.1020, 1.0990, 1.1000),
    ]

    result = MarketStructureService.detect_fvg(candles)

    assert result is not None
    assert result["type"] == "FVG_BEARISH"
    assert result["start_index"] == 4
    assert result["middle_index"] == 5
    assert result["end_index"] == 6
    assert result["lower_price"] == candles[6].high_price
    assert result["upper_price"] == candles[4].low_price
    assert result["timestamp"] == candles[6].timestamp


def test_detect_fvg_returns_none_without_gap_or_enough_candles():
    """Fewer than three candles or no strict gap must return None."""
    insufficient = [
        make_candle(0, 1.1000, 1.1020, 1.0990, 1.1010),
        make_candle(1, 1.1010, 1.1030, 1.1000, 1.1020),
    ]
    no_gap = [
        make_candle(0, 1.1000, 1.1020, 1.0990, 1.1010),
        make_candle(1, 1.1010, 1.1030, 1.1000, 1.1020),
        make_candle(2, 1.1020, 1.1040, 1.1020, 1.1030),
    ]

    assert MarketStructureService.detect_fvg(insufficient) is None
    assert MarketStructureService.detect_fvg(no_gap) is None

def test_detect_support_zone_from_nearby_swing_lows():
    """
    Nearby swing lows within tolerance must form
    one confirmed support zone.
    """

    swing_lows = [
        {
            "index": 2,
            "price": 1.1000,
            "timestamp": BASE_TIME + timedelta(hours=2),
        },
        {
            "index": 5,
            "price": 1.1003,
            "timestamp": BASE_TIME + timedelta(hours=5),
        },
        {
            "index": 8,
            "price": 1.1001,
            "timestamp": BASE_TIME + timedelta(hours=8),
        },
    ]

    result = MarketStructureService.detect_support_resistance_zones(
        [],
        swing_lows,
        tolerance=0.0005,
        min_touches=2,
    )

    assert len(result["support_zones"]) == 1
    assert len(result["resistance_zones"]) == 0

    zone = result["support_zones"][0]

    assert zone["type"] == "SUPPORT"
    assert zone["lower_price"] == 1.1000
    assert zone["upper_price"] == 1.1003
    assert zone["center_price"] == 1.100133
    assert zone["touch_count"] == 3
    assert zone["first_index"] == 2
    assert zone["last_index"] == 8


def test_detect_resistance_zone_from_nearby_swing_highs():
    """
    Nearby swing highs within tolerance must form
    one confirmed resistance zone.
    """

    swing_highs = [
        {
            "index": 3,
            "price": 1.1050,
            "timestamp": BASE_TIME + timedelta(hours=3),
        },
        {
            "index": 6,
            "price": 1.1052,
            "timestamp": BASE_TIME + timedelta(hours=6),
        },
        {
            "index": 9,
            "price": 1.1049,
            "timestamp": BASE_TIME + timedelta(hours=9),
        },
    ]

    result = MarketStructureService.detect_support_resistance_zones(
        swing_highs,
        [],
        tolerance=0.0005,
        min_touches=2,
    )

    assert len(result["support_zones"]) == 0
    assert len(result["resistance_zones"]) == 1

    zone = result["resistance_zones"][0]

    assert zone["type"] == "RESISTANCE"
    assert zone["lower_price"] == 1.1049
    assert zone["upper_price"] == 1.1052
    assert zone["center_price"] == 1.105033
    assert zone["touch_count"] == 3
    assert zone["first_index"] == 3
    assert zone["last_index"] == 9


def test_detect_support_resistance_keeps_distant_clusters_separate():
    """
    Swing points farther apart than tolerance
    must not be merged into one zone.
    """

    swing_lows = [
        {
            "index": 1,
            "price": 1.1000,
            "timestamp": BASE_TIME + timedelta(hours=1),
        },
        {
            "index": 3,
            "price": 1.1002,
            "timestamp": BASE_TIME + timedelta(hours=3),
        },
        {
            "index": 5,
            "price": 1.1040,
            "timestamp": BASE_TIME + timedelta(hours=5),
        },
        {
            "index": 7,
            "price": 1.1042,
            "timestamp": BASE_TIME + timedelta(hours=7),
        },
    ]

    result = MarketStructureService.detect_support_resistance_zones(
        [],
        swing_lows,
        tolerance=0.0005,
        min_touches=2,
    )

    assert len(result["support_zones"]) == 2

    first_zone = result["support_zones"][0]
    second_zone = result["support_zones"][1]

    assert first_zone["lower_price"] == 1.1000
    assert first_zone["upper_price"] == 1.1002
    assert first_zone["touch_count"] == 2

    assert second_zone["lower_price"] == 1.1040
    assert second_zone["upper_price"] == 1.1042
    assert second_zone["touch_count"] == 2


def test_detect_support_resistance_ignores_unconfirmed_single_touch():
    """
    A cluster with fewer touches than min_touches
    must not become a confirmed zone.
    """

    swing_highs = [
        {
            "index": 2,
            "price": 1.1050,
            "timestamp": BASE_TIME + timedelta(hours=2),
        }
    ]

    swing_lows = [
        {
            "index": 4,
            "price": 1.1000,
            "timestamp": BASE_TIME + timedelta(hours=4),
        }
    ]

    result = MarketStructureService.detect_support_resistance_zones(
        swing_highs,
        swing_lows,
        tolerance=0.0005,
        min_touches=2,
    )

    assert result["support_zones"] == []
    assert result["resistance_zones"] == []


def test_detect_support_resistance_includes_exact_tolerance_boundary():
    """
    A swing exactly tolerance distance from the
    current cluster center is part of that zone.
    """

    swing_lows = [
        {
            "index": 1,
            "price": 1.1000,
            "timestamp": BASE_TIME + timedelta(hours=1),
        },
        {
            "index": 3,
            "price": 1.1005,
            "timestamp": BASE_TIME + timedelta(hours=3),
        },
    ]

    result = MarketStructureService.detect_support_resistance_zones(
        [],
        swing_lows,
        tolerance=0.0005,
        min_touches=2,
    )

    assert len(result["support_zones"]) == 1

    zone = result["support_zones"][0]

    assert zone["lower_price"] == 1.1000
    assert zone["upper_price"] == 1.1005
    assert zone["center_price"] == 1.10025
    assert zone["touch_count"] == 2


def test_detect_support_resistance_uses_chronological_order():
    """
    Unordered swing input must still produce
    deterministic chronological zone metadata.
    """

    swing_highs = [
        {
            "index": 9,
            "price": 1.1051,
            "timestamp": BASE_TIME + timedelta(hours=9),
        },
        {
            "index": 2,
            "price": 1.1050,
            "timestamp": BASE_TIME + timedelta(hours=2),
        },
        {
            "index": 6,
            "price": 1.1052,
            "timestamp": BASE_TIME + timedelta(hours=6),
        },
    ]

    result = MarketStructureService.detect_support_resistance_zones(
        swing_highs,
        [],
        tolerance=0.0005,
        min_touches=2,
    )

    assert len(result["resistance_zones"]) == 1

    zone = result["resistance_zones"][0]

    assert zone["first_index"] == 2
    assert zone["last_index"] == 9
    assert zone["touch_count"] == 3
    assert zone["center_price"] == 1.1051

def test_detect_bullish_engulfing():
    """Bullish candle must engulf the previous bearish body."""

    candles = [
        make_candle(
            0,
            1.1020,
            1.1025,
            1.1005,
            1.1010,
        ),
        make_candle(
            1,
            1.1008,
            1.1030,
            1.1005,
            1.1025,
        ),
    ]

    result = (
        MarketStructureService
        .detect_engulfing(candles)
    )

    assert result is not None
    assert result["type"] == "ENGULFING_BULLISH"
    assert result["previous_index"] == 0
    assert result["engulfing_index"] == 1
    assert result["timestamp"] == candles[1].timestamp


def test_detect_bearish_engulfing():
    """Bearish candle must engulf the previous bullish body."""

    candles = [
        make_candle(
            0,
            1.1010,
            1.1025,
            1.1005,
            1.1020,
        ),
        make_candle(
            1,
            1.1022,
            1.1025,
            1.0995,
            1.1005,
        ),
    ]

    result = (
        MarketStructureService
        .detect_engulfing(candles)
    )

    assert result is not None
    assert result["type"] == "ENGULFING_BEARISH"
    assert result["previous_index"] == 0
    assert result["engulfing_index"] == 1
    assert result["timestamp"] == candles[1].timestamp


def test_detect_engulfing_returns_none_without_pattern():
    """Ordinary candles must not produce an engulfing signal."""

    candles = [
        make_candle(
            0,
            1.1000,
            1.1020,
            1.0995,
            1.1010,
        ),
        make_candle(
            1,
            1.1010,
            1.1020,
            1.1005,
            1.1015,
        ),
    ]

    result = (
        MarketStructureService
        .detect_engulfing(candles)
    )

    assert result is None


def test_detect_bullish_displacement():
    """Large bullish body relative to ATR is displacement."""

    candles = [
        make_candle(
            0,
            1.1000,
            1.1005,
            1.0998,
            1.1002,
        ),
        make_candle(
            1,
            1.1000,
            1.1020,
            1.0999,
            1.1018,
        ),
    ]

    result = (
        MarketStructureService
        .detect_displacement(
            candles,
            atr=0.0010,
            body_multiplier=1.5,
        )
    )

    assert result is not None
    assert result["type"] == "DISPLACEMENT_BULLISH"
    assert result["candle_index"] == 1
    assert result["body_size"] == 0.0018
    assert result["body_atr_ratio"] == 1.8
    assert result["timestamp"] == candles[1].timestamp


def test_detect_bearish_displacement():
    """Large bearish body relative to ATR is displacement."""

    candles = [
        make_candle(
            0,
            1.1020,
            1.1022,
            1.1015,
            1.1018,
        ),
        make_candle(
            1,
            1.1020,
            1.1021,
            1.0999,
            1.1002,
        ),
    ]

    result = (
        MarketStructureService
        .detect_displacement(
            candles,
            atr=0.0010,
            body_multiplier=1.5,
        )
    )

    assert result is not None
    assert result["type"] == "DISPLACEMENT_BEARISH"
    assert result["candle_index"] == 1
    assert result["body_size"] == 0.0018
    assert result["body_atr_ratio"] == 1.8


def test_detect_displacement_rejects_weak_candle():
    """Small candle body relative to ATR is not displacement."""

    candles = [
        make_candle(
            0,
            1.1000,
            1.1007,
            1.0998,
            1.1005,
        ),
    ]

    result = (
        MarketStructureService
        .detect_displacement(
            candles,
            atr=0.0010,
            body_multiplier=1.5,
        )
    )

    assert result is None


def test_detect_displacement_returns_none_for_invalid_atr():
    """Invalid ATR must not produce displacement."""

    candles = [
        make_candle(
            0,
            1.1000,
            1.1030,
            1.0995,
            1.1025,
        ),
    ]

    assert (
        MarketStructureService
        .detect_displacement(
            candles,
            atr=None,
        )
        is None
    )

    assert (
        MarketStructureService
        .detect_displacement(
            candles,
            atr=0,
        )
        is None
    )


def test_detect_displacement_returns_latest_event():
    """When several displacement candles exist, return latest."""

    candles = [
        make_candle(
            0,
            1.1000,
            1.1020,
            1.0999,
            1.1018,
        ),
        make_candle(
            1,
            1.1018,
            1.1020,
            1.1014,
            1.1016,
        ),
        make_candle(
            2,
            1.1018,
            1.1020,
            1.0995,
            1.1000,
        ),
    ]

    result = (
        MarketStructureService
        .detect_displacement(
            candles,
            atr=0.0010,
            body_multiplier=1.5,
        )
    )

    assert result is not None
    assert result["type"] == "DISPLACEMENT_BEARISH"
    assert result["candle_index"] == 2
    assert result["timestamp"] == candles[2].timestamp

# ==========================================================
# PREMIUM / DISCOUNT / EQUILIBRIUM
# ==========================================================


def test_detect_premium_discount_range():
    """
    A valid swing low followed by a swing high must create
    a dealing range with premium, equilibrium, and discount
    boundaries.
    """

    swing_lows = [
        {
            "index": 10,
            "price": 1.1000,
            "timestamp": BASE_TIME + timedelta(hours=10),
        },
    ]

    swing_highs = [
        {
            "index": 20,
            "price": 1.1100,
            "timestamp": BASE_TIME + timedelta(hours=20),
        },
    ]

    result = (
        MarketStructureService
        .detect_premium_discount(
            swing_highs,
            swing_lows,
        )
    )

    assert result is not None

    assert result["range_low"] == 1.1000
    assert result["range_high"] == 1.1100

    assert result["equilibrium"] == 1.1050

    assert result["discount_low"] == 1.1000
    assert result["discount_high"] == 1.1050

    assert result["premium_low"] == 1.1050
    assert result["premium_high"] == 1.1100

    assert result["low_index"] == 10
    assert result["high_index"] == 20


def test_detect_premium_discount_bearish_range():
    """
    The detector must also support a dealing range where
    the swing high occurs before the swing low.
    """

    swing_highs = [
        {
            "index": 10,
            "price": 1.1100,
            "timestamp": BASE_TIME + timedelta(hours=10),
        },
    ]

    swing_lows = [
        {
            "index": 20,
            "price": 1.1000,
            "timestamp": BASE_TIME + timedelta(hours=20),
        },
    ]

    result = (
        MarketStructureService
        .detect_premium_discount(
            swing_highs,
            swing_lows,
        )
    )

    assert result is not None

    assert result["range_low"] == 1.1000
    assert result["range_high"] == 1.1100
    assert result["equilibrium"] == 1.1050

    assert result["low_index"] == 20
    assert result["high_index"] == 10


def test_detect_premium_discount_uses_latest_swing_pair():
    """
    The latest available swing high and swing low must
    define the current visualization dealing range.
    """

    swing_highs = [
        {
            "index": 5,
            "price": 1.1200,
            "timestamp": BASE_TIME + timedelta(hours=5),
        },
        {
            "index": 30,
            "price": 1.1150,
            "timestamp": BASE_TIME + timedelta(hours=30),
        },
    ]

    swing_lows = [
        {
            "index": 8,
            "price": 1.0900,
            "timestamp": BASE_TIME + timedelta(hours=8),
        },
        {
            "index": 25,
            "price": 1.1050,
            "timestamp": BASE_TIME + timedelta(hours=25),
        },
    ]

    result = (
        MarketStructureService
        .detect_premium_discount(
            swing_highs,
            swing_lows,
        )
    )

    assert result is not None

    assert result["range_high"] == 1.1150
    assert result["range_low"] == 1.1050

    assert result["high_index"] == 30
    assert result["low_index"] == 25


def test_detect_premium_discount_returns_none_without_both_sides():
    """
    A dealing range requires at least one confirmed
    swing high and one confirmed swing low.
    """

    swing_highs = [
        {
            "index": 10,
            "price": 1.1100,
            "timestamp": BASE_TIME + timedelta(hours=10),
        },
    ]

    assert (
        MarketStructureService
        .detect_premium_discount(
            swing_highs,
            [],
        )
        is None
    )

    assert (
        MarketStructureService
        .detect_premium_discount(
            [],
            [],
        )
        is None
    )


def test_detect_premium_discount_rejects_zero_range():
    """
    Identical high and low prices do not form a valid
    dealing range.
    """

    swing_highs = [
        {
            "index": 10,
            "price": 1.1050,
            "timestamp": BASE_TIME + timedelta(hours=10),
        },
    ]

    swing_lows = [
        {
            "index": 20,
            "price": 1.1050,
            "timestamp": BASE_TIME + timedelta(hours=20),
        },
    ]

    result = (
        MarketStructureService
        .detect_premium_discount(
            swing_highs,
            swing_lows,
        )
    )

    assert result is None

# ==========================================================
# EQUAL HIGHS / EQUAL LOWS
# ==========================================================


def test_detect_equal_highs():
    """
    Multiple swing highs within tolerance must form
    one confirmed equal-high liquidity level.
    """

    swing_highs = [
        {
            "index": 10,
            "price": 1.1100,
            "timestamp": BASE_TIME + timedelta(hours=10),
        },
        {
            "index": 20,
            "price": 1.1101,
            "timestamp": BASE_TIME + timedelta(hours=20),
        },
        {
            "index": 30,
            "price": 1.11005,
            "timestamp": BASE_TIME + timedelta(hours=30),
        },
    ]

    result = (
        MarketStructureService
        .detect_equal_highs_lows(
            swing_highs,
            [],
            tolerance=0.0002,
            min_touches=2,
        )
    )

    assert result is not None

    assert len(result["equal_highs"]) == 1
    assert result["equal_lows"] == []

    level = result["equal_highs"][0]

    assert level["type"] == "EQUAL_HIGH"
    assert level["level_price"] == round(
        (1.1100 + 1.1101 + 1.11005) / 3,
        6,
    )
    assert level["touch_count"] == 3
    assert level["first_index"] == 10
    assert level["last_index"] == 30


def test_detect_equal_lows():
    """
    Multiple swing lows within tolerance must form
    one confirmed equal-low liquidity level.
    """

    swing_lows = [
        {
            "index": 5,
            "price": 1.1000,
            "timestamp": BASE_TIME + timedelta(hours=5),
        },
        {
            "index": 15,
            "price": 1.0999,
            "timestamp": BASE_TIME + timedelta(hours=15),
        },
        {
            "index": 25,
            "price": 1.10005,
            "timestamp": BASE_TIME + timedelta(hours=25),
        },
    ]

    result = (
        MarketStructureService
        .detect_equal_highs_lows(
            [],
            swing_lows,
            tolerance=0.0002,
            min_touches=2,
        )
    )

    assert result is not None

    assert result["equal_highs"] == []
    assert len(result["equal_lows"]) == 1

    level = result["equal_lows"][0]

    assert level["type"] == "EQUAL_LOW"
    assert level["level_price"] == round(
        (1.1000 + 1.0999 + 1.10005) / 3,
        6,
    )
    assert level["touch_count"] == 3
    assert level["first_index"] == 5
    assert level["last_index"] == 25


def test_equal_levels_ignore_single_touch():
    """
    A single swing point must not create an
    equal-high or equal-low liquidity level.
    """

    swing_highs = [
        {
            "index": 10,
            "price": 1.1100,
            "timestamp": BASE_TIME + timedelta(hours=10),
        },
    ]

    swing_lows = [
        {
            "index": 20,
            "price": 1.1000,
            "timestamp": BASE_TIME + timedelta(hours=20),
        },
    ]

    result = (
        MarketStructureService
        .detect_equal_highs_lows(
            swing_highs,
            swing_lows,
            tolerance=0.0002,
            min_touches=2,
        )
    )

    assert result == {
        "equal_highs": [],
        "equal_lows": [],
    }


def test_equal_levels_keep_distant_clusters_separate():
    """
    Swing points separated by more than tolerance
    must remain separate equal-level clusters.
    """

    swing_highs = [
        {
            "index": 10,
            "price": 1.1100,
            "timestamp": BASE_TIME + timedelta(hours=10),
        },
        {
            "index": 20,
            "price": 1.1101,
            "timestamp": BASE_TIME + timedelta(hours=20),
        },
        {
            "index": 30,
            "price": 1.1150,
            "timestamp": BASE_TIME + timedelta(hours=30),
        },
        {
            "index": 40,
            "price": 1.1151,
            "timestamp": BASE_TIME + timedelta(hours=40),
        },
    ]

    result = (
        MarketStructureService
        .detect_equal_highs_lows(
            swing_highs,
            [],
            tolerance=0.0002,
            min_touches=2,
        )
    )

    assert len(result["equal_highs"]) == 2
    assert result["equal_lows"] == []

    first_level = result["equal_highs"][0]
    second_level = result["equal_highs"][1]

    assert first_level["type"] == "EQUAL_HIGH"
    assert first_level["first_index"] == 10
    assert first_level["last_index"] == 20
    assert first_level["touch_count"] == 2

    assert second_level["type"] == "EQUAL_HIGH"
    assert second_level["first_index"] == 30
    assert second_level["last_index"] == 40
    assert second_level["touch_count"] == 2


def test_equal_levels_include_exact_tolerance_boundary():
    """
    A swing point exactly tolerance distance from
    the cluster must still belong to that level.
    """

    swing_lows = [
        {
            "index": 10,
            "price": 1.1000,
            "timestamp": BASE_TIME + timedelta(hours=10),
        },
        {
            "index": 20,
            "price": 1.1002,
            "timestamp": BASE_TIME + timedelta(hours=20),
        },
    ]

    result = (
        MarketStructureService
        .detect_equal_highs_lows(
            [],
            swing_lows,
            tolerance=0.0002,
            min_touches=2,
        )
    )

    assert result["equal_highs"] == []
    assert len(result["equal_lows"]) == 1

    level = result["equal_lows"][0]

    assert level["type"] == "EQUAL_LOW"
    assert level["level_price"] == 1.1001
    assert level["touch_count"] == 2
    assert level["first_index"] == 10
    assert level["last_index"] == 20


def test_equal_levels_use_chronological_order():
    """
    Unordered swing input must still produce
    deterministic chronological metadata.
    """

    swing_highs = [
        {
            "index": 30,
            "price": 1.11005,
            "timestamp": BASE_TIME + timedelta(hours=30),
        },
        {
            "index": 10,
            "price": 1.1100,
            "timestamp": BASE_TIME + timedelta(hours=10),
        },
        {
            "index": 20,
            "price": 1.1101,
            "timestamp": BASE_TIME + timedelta(hours=20),
        },
    ]

    result = (
        MarketStructureService
        .detect_equal_highs_lows(
            swing_highs,
            [],
            tolerance=0.0002,
            min_touches=2,
        )
    )

    assert len(result["equal_highs"]) == 1

    level = result["equal_highs"][0]

    assert level["type"] == "EQUAL_HIGH"
    assert level["first_index"] == 10
    assert level["last_index"] == 30
    assert level["touch_count"] == 3