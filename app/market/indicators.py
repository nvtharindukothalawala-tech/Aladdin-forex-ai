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
    def calculate_rsi(prices, period):
        """
        Calculate Relative Strength Index (RSI).

        RSI measures market momentum.

        RSI > 70:
            Possible overbought condition.

        RSI < 30:
            Possible oversold condition.

        Args:
            prices:
                List of closing prices.

            period:
                RSI calculation period.

        Returns:
            float:
                RSI value.

        Raises:
            ValueError:
                If insufficient price data.
        """

        if len(prices) <= period:
            raise ValueError("Not enough price data for RSI calculation.")

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

        average_gain = sum(gains[:period]) / period

        average_loss = sum(losses[:period]) / period

        if average_loss == 0:
            return 100.0

        relative_strength = average_gain / average_loss

        rsi = 100 - (100 / (1 + relative_strength))

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
