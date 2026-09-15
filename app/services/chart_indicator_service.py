"""
chart_indicator_service.py

Provides timestamp-aligned technical indicator series
for the ALADDIN V2 professional trading chart.

This service operates only on candle data that has
already been retrieved from MetaTrader 5.

It does not connect to MT5, execute trades, modify
positions, or change ALADDIN AI decision authority.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from app.market.candle import Candle
from app.market.indicators import TechnicalIndicators


class ChartIndicatorService:
    """
    Calculate technical indicator series for
    ALADDIN V2 chart visualization.

    These series are visualization data only.

    The existing TechnicalIndicators and
    MarketAnalysisService remain authoritative
    for the validated AI technical-analysis pipeline.

    RSI and ADX chart-series calculations preserve
    the exact existing ALADDIN indicator semantics
    while avoiding repeated full-prefix calculations.
    """

    # ======================================================
    # EMA SERIES
    # ======================================================

    @staticmethod
    def calculate_ema_series(
        candles: list[Candle],
        period: int = 20,
    ) -> list[dict]:
        """
        Calculate a timestamp-aligned Exponential
        Moving Average series.

        The initial EMA is seeded using the SMA of
        the first ``period`` closing prices.

        Therefore the first EMA point corresponds
        to candle index ``period - 1``.

        Args:
            candles:
                Chronologically ordered Candle objects.

            period:
                EMA period. ALADDIN currently uses
                EMA 20 for technical analysis.

        Returns:
            List of dictionaries containing:

            {
                "time": Unix timestamp,
                "value": EMA value
            }

        Raises:
            ValueError:
                If the period is invalid or there are
                not enough candles.
        """

        if period <= 0:
            raise ValueError(
                "EMA period must be greater than zero."
            )

        if len(candles) < period:
            raise ValueError(
                "Not enough candle data for EMA series calculation."
            )

        closing_prices = [
            candle.close_price
            for candle in candles
        ]

        multiplier = 2 / (period + 1)

        # --------------------------------------------------
        # Initial EMA
        # --------------------------------------------------

        ema = (
            sum(closing_prices[:period])
            / period
        )

        series = [
            {
                "time": int(
                    candles[
                        period - 1
                    ].timestamp.timestamp()
                ),
                "value": round(
                    ema,
                    6,
                ),
            }
        ]

        # --------------------------------------------------
        # Remaining EMA values
        # --------------------------------------------------

        for index in range(
            period,
            len(candles),
        ):
            price = closing_prices[index]

            ema = (
                (price - ema)
                * multiplier
            ) + ema

            series.append(
                {
                    "time": int(
                        candles[
                            index
                        ].timestamp.timestamp()
                    ),
                    "value": round(
                        ema,
                        6,
                    ),
                }
            )

        return series

    # ======================================================
    # RSI SERIES
    # ======================================================

    @staticmethod
    def calculate_rsi_series(
        candles: list[Candle],
        period: int = 14,
    ) -> list[dict]:
        """
        Calculate a timestamp-aligned RSI series while
        preserving the exact behavior of ALADDIN's
        existing TechnicalIndicators.calculate_rsi().

        The authoritative RSI implementation calculates
        its average gain and average loss from the first
        ``period`` price changes. Additional prices do
        not alter those averages.

        Therefore the authoritative RSI value can be
        calculated once using the first valid
        ``period + 1`` prices and reused for every
        subsequent chart timestamp.

        This is intentionally compatibility-preserving.
        It does not replace ALADDIN's current RSI formula
        with a different rolling or Wilder RSI formula.

        The first RSI point corresponds to candle index
        ``period``.

        Args:
            candles:
                Chronologically ordered Candle objects.

            period:
                RSI period. ALADDIN currently uses
                RSI 14 for technical analysis.

        Returns:
            List of timestamp/value dictionaries.

        Raises:
            ValueError:
                If the period is invalid or there are
                not enough candles.
        """

        if period <= 0:
            raise ValueError(
                "RSI period must be greater than zero."
            )

        if len(candles) <= period:
            raise ValueError(
                "Not enough candle data for RSI series calculation."
            )

        closing_prices = [
            candle.close_price
            for candle in candles
        ]

        # --------------------------------------------------
        # Authoritative RSI value
        # --------------------------------------------------
        #
        # TechnicalIndicators.calculate_rsi() uses only
        # the first ``period`` changes when calculating
        # average gain and average loss.
        #
        # Calling it once on the first valid prefix gives
        # exactly the same value that it returns for every
        # longer prefix under the existing implementation.
        # --------------------------------------------------

        rsi = (
            TechnicalIndicators
            .calculate_rsi(
                closing_prices[
                    : period + 1
                ],
                period,
            )
        )

        return [
            {
                "time": int(
                    candles[
                        index
                    ].timestamp.timestamp()
                ),
                "value": rsi,
            }
            for index in range(
                period,
                len(candles),
            )
        ]

    # ======================================================
    # ADX SERIES
    # ======================================================

    @staticmethod
    def calculate_adx_series(
        candles: list[Candle],
        period: int = 14,
    ) -> list[dict]:
        """
        Calculate a timestamp-aligned ADX series while
        preserving the exact behavior of ALADDIN's
        existing TechnicalIndicators.calculate_adx().

        The authoritative implementation:

        1. calculates True Range, +DM and -DM,
        2. initializes their Wilder averages,
        3. calculates DX before applying the current
           smoothing update,
        4. updates the Wilder averages,
        5. returns the arithmetic mean of all DX values.

        This chart implementation performs those same
        operations once in chronological order and keeps
        a running DX sum and count.

        Therefore each emitted chart point is equivalent
        to calling TechnicalIndicators.calculate_adx()
        on the candle prefix ending at that timestamp,
        without repeatedly recalculating the complete
        history.

        The first ADX point corresponds to candle index
        ``(period * 2) - 1``.

        Args:
            candles:
                Chronologically ordered Candle objects.

            period:
                ADX period. ALADDIN currently uses
                ADX 14 for technical analysis.

        Returns:
            List of timestamp/value dictionaries.

        Raises:
            ValueError:
                If the period is invalid or there are
                not enough candles.
        """

        if period <= 0:
            raise ValueError(
                "ADX period must be greater than zero."
            )

        minimum_candles = (
            period * 2
        )

        if len(candles) < minimum_candles:
            raise ValueError(
                "Not enough candle data for ADX series calculation."
            )

        true_ranges = []
        plus_dm = []
        minus_dm = []

        # --------------------------------------------------
        # True Range and Directional Movement
        # --------------------------------------------------
        #
        # This intentionally mirrors
        # TechnicalIndicators.calculate_adx().
        # --------------------------------------------------

        for index in range(
            1,
            len(candles),
        ):
            current = candles[index]
            previous = candles[
                index - 1
            ]

            high_low = (
                current.high_price
                - current.low_price
            )

            high_previous_close = abs(
                current.high_price
                - previous.close_price
            )

            low_previous_close = abs(
                current.low_price
                - previous.close_price
            )

            true_range = max(
                high_low,
                high_previous_close,
                low_previous_close,
            )

            true_ranges.append(
                true_range
            )

            upward_move = (
                current.high_price
                - previous.high_price
            )

            downward_move = (
                previous.low_price
                - current.low_price
            )

            if (
                upward_move > downward_move
                and upward_move > 0
            ):
                plus_dm.append(
                    upward_move
                )
            else:
                plus_dm.append(
                    0.0
                )

            if (
                downward_move > upward_move
                and downward_move > 0
            ):
                minus_dm.append(
                    downward_move
                )
            else:
                minus_dm.append(
                    0.0
                )

        # --------------------------------------------------
        # Initial Wilder averages
        # --------------------------------------------------
        #
        # Keep the same arithmetic and operation order
        # used by TechnicalIndicators.calculate_adx().
        # --------------------------------------------------

        atr = (
            sum(
                true_ranges[:period]
            )
            / period
        )

        smoothed_plus_dm = (
            sum(
                plus_dm[:period]
            )
            / period
        )

        smoothed_minus_dm = (
            sum(
                minus_dm[:period]
            )
            / period
        )

        # --------------------------------------------------
        # Incremental DX / prefix ADX
        # --------------------------------------------------

        series = []

        dx_sum = 0.0
        dx_count = 0

        # A true-range index corresponds to the candle
        # immediately after it. For example, TR index 0
        # belongs to candle index 1.
        #
        # TechnicalIndicators starts its DX loop at
        # ``period``.
        for index in range(
            period,
            len(true_ranges),
        ):

            # ----------------------------------------------
            # Calculate DX BEFORE current smoothing update.
            #
            # This ordering exactly matches the existing
            # TechnicalIndicators implementation.
            # ----------------------------------------------

            if atr == 0:
                dx = 0.0

            else:
                plus_di = (
                    100
                    * smoothed_plus_dm
                    / atr
                )

                minus_di = (
                    100
                    * smoothed_minus_dm
                    / atr
                )

                denominator = (
                    plus_di
                    + minus_di
                )

                if denominator == 0:
                    dx = 0.0

                else:
                    dx = (
                        100
                        * abs(
                            plus_di
                            - minus_di
                        )
                        / denominator
                    )

            dx_sum += dx
            dx_count += 1

            # ----------------------------------------------
            # Wilder smoothing
            # ----------------------------------------------

            atr = (
                (
                    atr
                    * (period - 1)
                )
                + true_ranges[index]
            ) / period

            smoothed_plus_dm = (
                (
                    smoothed_plus_dm
                    * (period - 1)
                )
                + plus_dm[index]
            ) / period

            smoothed_minus_dm = (
                (
                    smoothed_minus_dm
                    * (period - 1)
                )
                + minus_dm[index]
            ) / period

            # ----------------------------------------------
            # Emit only once the authoritative ADX method
            # has enough candles.
            #
            # Current TR index:
            #     index
            #
            # Corresponding candle:
            #     index + 1
            #
            # First valid ADX candle:
            #     (period * 2) - 1
            # ----------------------------------------------

            candle_index = (
                index + 1
            )

            if (
                candle_index
                >= minimum_candles - 1
            ):
                adx = (
                    dx_sum
                    / dx_count
                )

                series.append(
                    {
                        "time": int(
                            candles[
                                candle_index
                            ].timestamp.timestamp()
                        ),
                        "value": round(
                            adx,
                            2,
                        ),
                    }
                )

        if not series:
            raise ValueError(
                "Unable to calculate ADX."
            )

        return series