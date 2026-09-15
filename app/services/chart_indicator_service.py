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


class ChartIndicatorService:
    """
    Calculate technical indicator series for
    ALADDIN V2 chart visualization.

    These series are visualization data only.

    The existing TechnicalIndicators and
    MarketAnalysisService remain authoritative
    for the validated AI technical-analysis pipeline.
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