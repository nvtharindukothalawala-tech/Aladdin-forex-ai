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


# ==========================================================
# EMA SERIES
# ==========================================================


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


# ==========================================================
# RSI SERIES
# ==========================================================


def test_rsi_series_starts_after_warmup_period():
    """
    RSI requires period + 1 prices.

    RSI14 should therefore start at candle index 14.
    """

    prices = [
        1.1000 + (
            (index % 5) * 0.001
        )
        for index in range(25)
    ]

    candles = _create_candles(prices)

    series = (
        ChartIndicatorService
        .calculate_rsi_series(
            candles,
            period=14,
        )
    )

    assert len(series) == 11

    assert series[0]["time"] == int(
        candles[14].timestamp.timestamp()
    )

    assert series[-1]["time"] == int(
        candles[-1].timestamp.timestamp()
    )


def test_rsi_series_latest_value_matches_existing_indicator():
    """
    The latest chart RSI must match ALADDIN's
    existing RSI calculation for the same data.
    """

    prices = [
        1.1000,
        1.1010,
        1.1005,
        1.1020,
        1.1010,
        1.1030,
        1.1025,
        1.1040,
        1.1030,
        1.1050,
        1.1045,
        1.1060,
        1.1050,
        1.1070,
        1.1065,
        1.1080,
        1.1070,
        1.1090,
        1.1085,
        1.1100,
    ]

    candles = _create_candles(prices)

    series = (
        ChartIndicatorService
        .calculate_rsi_series(
            candles,
            period=14,
        )
    )

    existing_rsi = (
        TechnicalIndicators.calculate_rsi(
            prices,
            14,
        )
    )

    assert (
        series[-1]["value"]
        == existing_rsi
    )


def test_rsi_series_values_match_existing_indicator_for_each_prefix():
    """
    Every chart RSI point must preserve the existing
    ALADDIN RSI calculation for its candle prefix.
    """

    prices = [
        1.2000 + (
            ((index * 3) % 7) * 0.0005
        )
        for index in range(24)
    ]

    candles = _create_candles(prices)

    period = 5

    series = (
        ChartIndicatorService
        .calculate_rsi_series(
            candles,
            period=period,
        )
    )

    for point_index, point in enumerate(
        series,
        start=period,
    ):
        expected = (
            TechnicalIndicators.calculate_rsi(
                prices[: point_index + 1],
                period,
            )
        )

        assert point["time"] == int(
            candles[
                point_index
            ].timestamp.timestamp()
        )

        assert point["value"] == expected


def test_rsi_series_handles_zero_average_loss():
    """
    A continuously rising market should preserve
    the existing RSI behavior and return 100.
    """

    prices = [
        1.1000 + (index * 0.001)
        for index in range(20)
    ]

    candles = _create_candles(prices)

    series = (
        ChartIndicatorService
        .calculate_rsi_series(
            candles,
            period=14,
        )
    )

    assert series[-1]["value"] == 100.0


def test_rsi_series_rejects_insufficient_candles():
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
            "RSI series calculation."
        ),
    ):
        (
            ChartIndicatorService
            .calculate_rsi_series(
                candles,
                period=14,
            )
        )


def test_rsi_series_rejects_invalid_period():
    candles = _create_candles(
        [
            1.1000,
            1.1010,
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "RSI period must be greater "
            "than zero."
        ),
    ):
        (
            ChartIndicatorService
            .calculate_rsi_series(
                candles,
                period=0,
            )
        )


# ==========================================================
# ADX SERIES
# ==========================================================


def test_adx_series_starts_after_warmup_period():
    """
    Existing ALADDIN ADX requires at least
    period * 2 candles.

    ADX14 should therefore start at candle index 27.
    """

    prices = [
        1.1000 + (
            (index * 0.0007)
            + ((index % 4) * 0.0002)
        )
        for index in range(35)
    ]

    candles = _create_candles(prices)

    series = (
        ChartIndicatorService
        .calculate_adx_series(
            candles,
            period=14,
        )
    )

    assert len(series) == 8

    assert series[0]["time"] == int(
        candles[27].timestamp.timestamp()
    )

    assert series[-1]["time"] == int(
        candles[-1].timestamp.timestamp()
    )


def test_adx_series_latest_value_matches_existing_indicator():
    """
    The latest chart ADX must match ALADDIN's
    existing ADX calculation for the same candles.
    """

    prices = [
        1.1000 + (
            (index * 0.0004)
            + ((index % 6) * 0.0003)
        )
        for index in range(40)
    ]

    candles = _create_candles(prices)

    series = (
        ChartIndicatorService
        .calculate_adx_series(
            candles,
            period=14,
        )
    )

    existing_adx = (
        TechnicalIndicators.calculate_adx(
            candles,
            14,
        )
    )

    assert (
        series[-1]["value"]
        == existing_adx
    )


def test_adx_series_values_match_existing_indicator_for_each_prefix():
    """
    Every chart ADX point must preserve the existing
    ALADDIN ADX calculation for its candle prefix.
    """

    prices = [
        1.2000 + (
            (index * 0.0003)
            + ((index % 5) * 0.0004)
        )
        for index in range(18)
    ]

    candles = _create_candles(prices)

    period = 5

    series = (
        ChartIndicatorService
        .calculate_adx_series(
            candles,
            period=period,
        )
    )

    for point_index, point in enumerate(
        series,
        start=(period * 2) - 1,
    ):
        expected = (
            TechnicalIndicators.calculate_adx(
                candles[: point_index + 1],
                period,
            )
        )

        assert point["time"] == int(
            candles[
                point_index
            ].timestamp.timestamp()
        )

        assert point["value"] == expected


def test_adx_series_rejects_insufficient_candles():
    candles = _create_candles(
        [
            1.1000 + (index * 0.001)
            for index in range(10)
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "Not enough candle data for "
            "ADX series calculation."
        ),
    ):
        (
            ChartIndicatorService
            .calculate_adx_series(
                candles,
                period=14,
            )
        )


def test_adx_series_rejects_invalid_period():
    candles = _create_candles(
        [
            1.1000,
            1.1010,
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "ADX period must be greater "
            "than zero."
        ),
    ):
        (
            ChartIndicatorService
            .calculate_adx_series(
                candles,
                period=0,
            )
        )