"""
market_analysis_service.py

Connects MetaTrader 5 market data with
Aladdin technical analysis.

Author: Tharindu Kothalawala
Project: Aladdin
"""

import MetaTrader5 as mt5

from app.analysis.market_analyzer import MarketAnalyzer
from app.market.indicators import TechnicalIndicators
from app.market.mt5_provider import MT5DataProvider


class MarketAnalysisService:
    """
    Provides complete market analysis using
    real MetaTrader 5 market data.
    """

    def __init__(self):
        """
        Create the market analysis service.
        """

        self.provider = MT5DataProvider()

    def analyze(
        self,
        symbol,
        timeframe=mt5.TIMEFRAME_H1,
        candle_count=1000,
    ):
        """
        Get market data and perform technical analysis.

        Args:
            symbol:
                MT5 symbol, for example EURUSD.

            timeframe:
                MT5 timeframe.

            candle_count:
                Number of candles used for analysis.

        Returns:
            MarketSignal containing the analysis.
        """

        candles = self.provider.get_candles(
            symbol=symbol,
            timeframe=timeframe,
            count=candle_count,
        )

        if not candles:
            raise ValueError(
                f"No market candles available for {symbol}."
            )

        prices = [
            candle.close_price
            for candle in candles
        ]

        # Calculate technical indicators

        ema = TechnicalIndicators.calculate_ema(
            prices,
            20,
        )

        rsi = TechnicalIndicators.calculate_rsi(
            prices,
            14,
        )

        atr = TechnicalIndicators.calculate_atr(
            candles,
            14,
        )

        adx = TechnicalIndicators.calculate_adx(
            candles,
            14,
        )

        # Latest closing price

        current_price = candles[-1].close_price

        # Generate market signal

        signal = MarketAnalyzer.analyze(
            symbol=symbol,
            current_price=current_price,
            ema=ema,
            rsi=rsi,
            atr=atr,
            adx=adx,
        )

        return signal

    def close(self):
        """
        Close the MetaTrader 5 connection.
        """

        self.provider.disconnect()