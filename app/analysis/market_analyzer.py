"""
market_analyzer.py

Analyzes market conditions using
technical indicators.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.analysis.signal import MarketSignal


class MarketAnalyzer:
    """
    Analyze market data and create trading insights.
    """

    @staticmethod
    def analyze(
        symbol,
        current_price,
        sma,
        rsi,
        atr,
    ):
        """
        Generate market analysis.

        Rules:

        Price > SMA:
            Bullish trend

        Price < SMA:
            Bearish trend

        RSI:
            Momentum

        ATR:
            Volatility
        """

        # Trend detection
        if current_price > sma:
            trend = "Bullish"

        else:
            trend = "Bearish"

        # Momentum detection
        if rsi >= 70:
            momentum = "Overbought"

        elif rsi <= 30:
            momentum = "Oversold"

        elif rsi >= 50:
            momentum = "Positive"

        else:
            momentum = "Negative"

        # Volatility detection
        if atr > 0.002:
            volatility = "High"

        else:
            volatility = "Normal"

        explanation = f"Price is {trend.lower()} " f"with {momentum.lower()} momentum."

        return MarketSignal(
            symbol=symbol,
            trend=trend,
            momentum=momentum,
            volatility=volatility,
            explanation=explanation,
        )
