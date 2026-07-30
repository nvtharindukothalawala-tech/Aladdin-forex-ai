"""
candle.py

Contains the Candle model used to represent
Forex OHLC market data.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Candle:
    """
    Represents one Forex price candle.

    OHLC:

    Open  - first price
    High  - highest price
    Low   - lowest price
    Close - last price
    """

    symbol: str

    timeframe: str

    open_price: float

    high_price: float

    low_price: float

    close_price: float

    volume: float

    timestamp: datetime

    def price_range(self):
        """
        Calculate candle movement range.

        Formula:

        High - Low
        """

        return round(
            self.high_price - self.low_price,
            6,
        )

    def is_bullish(self):
        """
        Check whether candle closed higher
        than it opened.
        """

        return self.close_price > self.open_price

    def is_bearish(self):
        """
        Check whether candle closed lower
        than it opened.
        """

        return self.close_price < self.open_price
