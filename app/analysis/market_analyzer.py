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
        ema,
        rsi,
        atr,
        adx,
    ):
        """
        Generate market analysis.

        Rules:

        Price > EMA:
            Bullish trend

        Price < EMA:
            Bearish trend

        RSI:
            Momentum

        ATR:
            Volatility

        ADX:
            Trend strength
        """

        # Trend detection
        if current_price > ema:
            trend = "Bullish"

        elif current_price < ema:
            trend = "Bearish"

        else:
            trend = "Neutral"

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

        # Trend strength
        if adx >= 25:
            trend_strength = "Strong"

        elif adx >= 20:
            trend_strength = "Developing"

        else:
            trend_strength = "Weak"

        explanation = (
            f"Price is {trend.lower()} with "
            f"{momentum.lower()} momentum and "
            f"{trend_strength.lower()} trend strength."
        )

        return MarketSignal(
            symbol=symbol,
            trend=trend,
            momentum=momentum,
            volatility=volatility,
            ema=ema,
            rsi=rsi,
            atr=atr,
            adx=adx,
            explanation=explanation,
        )