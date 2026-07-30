"""
data_provider.py

Contains MarketDataProvider used by
the Aladdin Forex Trading Assistant.

This class stores and provides
market candle data.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.market.candle import Candle


class MarketDataProvider:
    """
    Manage market candle data.

    This class is the bridge between
    market data and technical analysis.
    """

    def __init__(self):
        """
        Create empty candle storage.
        """

        self.candles = []

    def add_candle(self, candle: Candle):
        """
        Add a candle to storage.

        Args:
            candle:
                Candle object.
        """

        self.candles.append(candle)

    def get_all_candles(self):
        """
        Return all stored candles.
        """

        return self.candles

    def get_latest(self, symbol, timeframe):
        """
        Get the latest candle
        for a symbol and timeframe.
        """

        candles = [
            candle
            for candle in self.candles
            if candle.symbol == symbol and candle.timeframe == timeframe
        ]

        if not candles:
            return None

        return candles[-1]

    def get_history(self, symbol, timeframe):
        """
        Get candle history
        for a symbol and timeframe.
        """

        return [
            candle
            for candle in self.candles
            if candle.symbol == symbol and candle.timeframe == timeframe
        ]
