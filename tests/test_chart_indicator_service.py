"""
test_chart_indicator_service.py

Tests for ALADDIN V2 chart indicator series.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.market.candle import Candle
from app.market.indicators import TechnicalIndicators
from app.services.chart_indicator_service import (
    ChartIndicatorService,
)


def _create_candles(
    closing_prices: list[float],
) -> list[Candle]:
    """
    Create deterministic candles for indicator tests.
    """

    start_time = datetime(
        2026,
        1,
        1,
        0,
        0,
        tzinfo=timezone.utc,
    )

    candles = []

    for index, close_price in enumerate(
        closing_prices
    ):
        candles.append(
            Candle(
                symbol="EURUSD",
                timeframe="H1",
                open_price=close_price - 0.001,
                high_price=close_price + 0.002,
                low_price=close_price - 0.002,
                close_price=close_price,
                volume=1000,
                timestamp=(
                    start_time
                    + timedelta(hours=index)
                ),
            )
        )

    return candles


def test_ema_series_starts_after_warmup_period():
    """
    EMA20 should start at candle index 19.
    """

    prices = [
        1.1000 + (index * 0.001)
        for index in range(25)
    ]

    candles = _create_candles(prices)

    series = (
        ChartIndicatorService
        .calculate_ema_series(
            candles,
            period=20,
        )
    )

    assert len(series) == 6

    assert series[0]["time"] == int(
        candles[19].timestamp.timestamp()
    )

    assert series[-1]["time"] == int(
        candles[-1].timestamp.timestamp()
    )


def test_ema_series_initial_value_is_sma_seed():
    """
    The first EMA value should equal the SMA
    of the first period closing prices.
    """

    prices = [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
    ]

    candles = _create_candles(prices)

    series = (
        ChartIndicatorService
        .calculate_ema_series(
            candles,
            period=3,
        )
    )

    assert series[0]["value"] == 2.0


def test_ema_series_latest_value_matches_existing_indicator():
    """
    The latest chart EMA must match ALADDIN's
    existing EMA calculation for the same data.
    """

    prices = [
        1.1000 + (index * 0.0005)
        for index in range(30)
    ]

    candles = _create_candles(prices)

    series = (
        ChartIndicatorService
        .calculate_ema_series(
            candles,
            period=20,
        )
    )

    existing_ema = (
        TechnicalIndicators.calculate_ema(
            prices,
            20,
        )
    )

    assert (
        series[-1]["value"]
        == existing_ema
    )


def test_ema_series_timestamps_remain_aligned():
    """
    Every EMA point must use the timestamp
    of its corresponding source candle.
    """

    prices = [
        1.2000 + (index * 0.001)
        for index in range(10)
    ]

    candles = _create_candles(prices)

    series = (
        ChartIndicatorService
        .calculate_ema_series(
            candles,
            period=5,
        )
    )

    expected_times = [
        int(candle.timestamp.timestamp())
        for candle in candles[4:]
    ]

    actual_times = [
        point["time"]
        for point in series
    ]

    assert actual_times == expected_times


def test_ema_series_rejects_insufficient_candles():
    candles = _create_candles(
        [
            1.1000,
            1.1010,
            1.1020,
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "Not enough candle data for "
            "EMA series calculation."
        ),
    ):
        (
            ChartIndicatorService
            .calculate_ema_series(
                candles,
                period=20,
            )
        )


def test_ema_series_rejects_invalid_period():
    candles = _create_candles(
        [
            1.1000,
            1.1010,
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "EMA period must be greater "
            "than zero."
        ),
    ):
        (
            ChartIndicatorService
            .calculate_ema_series(
                candles,
                period=0,
            )
        )