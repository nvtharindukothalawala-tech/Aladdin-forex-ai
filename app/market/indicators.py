"""
indicators.py

Contains technical indicators used by
the Aladdin Forex Trading Assistant.

Author: Tharindu Kothalwala
Project: Aladdin
"""


class TechnicalIndicators:
    """
    Calculate technical indicators
    from market candle data.
    """

    @staticmethod
    def calculate_sma(prices, period):
        """
        Calculate Simple Moving Average.

        Args:
            prices:
                List of closing prices.

            period:
                Number of prices used for calculation.

        Returns:
            float:
                SMA value.

        Raises:
            ValueError:
                If insufficient data is provided.
        """

        if len(prices) < period:
            raise ValueError("Not enough price data for SMA calculation.")

        selected_prices = prices[-period:]

        sma = sum(selected_prices) / period

        return round(
            sma,
            6,
        )

    @staticmethod
    def calculate_ema(prices, period):
        """
        Calculate Exponential Moving Average.

        EMA gives more importance to recent prices.

        Args:
            prices:
                List of closing prices.

            period:
                Number of prices used for calculation.

        Returns:
            float:
                EMA value.

        Raises:
            ValueError:
                If insufficient data is provided.
        """

        if len(prices) < period:
            raise ValueError(
                "Not enough price data for EMA calculation."
            )

        multiplier = 2 / (period + 1)

        ema = sum(prices[:period]) / period

        for price in prices[period:]:
            ema = (
                (price - ema) * multiplier
            ) + ema

        return round(
            ema,
            6,
        )

    @staticmethod
    def calculate_rsi(prices, period):
        """
        Calculate Relative Strength Index (RSI).

        RSI measures market momentum.

        RSI > 70:
            Possible overbought condition.

        RSI < 30:
            Possible oversold condition.
        """

        if len(prices) <= period:
            raise ValueError(
                "Not enough price data for RSI calculation."
            )

        gains = []
        losses = []

        for index in range(1, len(prices)):
            change = prices[index] - prices[index - 1]

            if change > 0:
                gains.append(change)
                losses.append(0)

            else:
                gains.append(0)
                losses.append(abs(change))

        average_gain = sum(
            gains[:period]
        ) / period

        average_loss = sum(
            losses[:period]
        ) / period

        if average_loss == 0:
            return 100.0

        relative_strength = (
            average_gain / average_loss
        )

        rsi = 100 - (
            100 / (1 + relative_strength)
        )

        return round(
            rsi,
            2,
        )

    @staticmethod
    def calculate_atr(candles, period):
        """
        Calculate Average True Range (ATR).

        ATR measures market volatility.

        Args:
            candles:
                List of Candle objects.

            period:
                ATR calculation period.

        Returns:
            float:
                ATR value.

        Raises:
            ValueError:
                If insufficient candle data.
        """

        if len(candles) <= period:
            raise ValueError("Not enough candle data for ATR calculation.")

        true_ranges = []

        for index in range(1, len(candles)):

            current = candles[index]

            previous = candles[index - 1]

            high_low = current.high_price - current.low_price

            high_previous_close = abs(current.high_price - previous.close_price)

            low_previous_close = abs(current.low_price - previous.close_price)

            true_range = max(
                high_low,
                high_previous_close,
                low_previous_close,
            )

            true_ranges.append(true_range)

        atr = sum(true_ranges[:period]) / period

        return round(
            atr,
            6,
        )

    @staticmethod
    def calculate_adx(candles, period):
        """
        Calculate Average Directional Index (ADX).

        ADX measures the strength of a market trend.

        ADX below 20:
            Weak trend.

        ADX between 20 and 25:
            Developing trend.

        ADX above 25:
            Stronger trend.

        Args:
            candles:
                List of Candle objects.

            period:
                ADX calculation period.

        Returns:
            float:
                ADX value.

        Raises:
            ValueError:
                If insufficient candle data is provided.
        """

        if len(candles) < (period * 2):
            raise ValueError(
                "Not enough candle data for ADX calculation."
            )

        true_ranges = []
        plus_dm = []
        minus_dm = []

        # ------------------------------------------
        # Calculate True Range and Directional Move
        # ------------------------------------------

        for index in range(1, len(candles)):

            current = candles[index]
            previous = candles[index - 1]

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

            true_ranges.append(true_range)

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
                plus_dm.append(upward_move)
            else:
                plus_dm.append(0.0)

            if (
                downward_move > upward_move
                and downward_move > 0
            ):
                minus_dm.append(downward_move)
            else:
                minus_dm.append(0.0)

        # ------------------------------------------
        # Initial Wilder averages
        # ------------------------------------------

        atr = (
            sum(true_ranges[:period])
            / period
        )

        smoothed_plus_dm = (
            sum(plus_dm[:period])
            / period
        )

        smoothed_minus_dm = (
            sum(minus_dm[:period])
            / period
        )

        dx_values = []

        # ------------------------------------------
        # Calculate DX values
        # ------------------------------------------

        for index in range(
            period,
            len(true_ranges),
        ):

            if atr == 0:
                dx_values.append(0.0)

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
                    plus_di + minus_di
                )

                if denominator == 0:
                    dx = 0.0

                else:
                    dx = (
                        100
                        * abs(
                            plus_di - minus_di
                        )
                        / denominator
                    )

                dx_values.append(dx)

            # ----------------------------------
            # Wilder smoothing
            # ----------------------------------

            atr = (
                (
                    atr * (period - 1)
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

        if not dx_values:
            raise ValueError(
                "Unable to calculate ADX."
            )

        # ------------------------------------------
        # Calculate ADX
        # ------------------------------------------

        adx = sum(dx_values) / len(dx_values)

        return round(
            adx,
            2,
        )