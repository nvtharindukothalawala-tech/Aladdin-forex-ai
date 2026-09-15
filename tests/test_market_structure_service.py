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