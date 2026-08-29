"""
market_analyzer.py

Analyzes market conditions using
technical indicators.

Author: Tharindu Kothalawala
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
        ema=None,
        rsi=None,
        atr=None,
        adx=None,
        sma=None,
    ):
        """
        Generate market analysis.

        Backward compatibility:

        Older callers may provide:
            sma
            rsi
            atr

        Newer callers may provide:
            ema
            rsi
            atr
            adx

        If EMA is not provided, SMA is used as the
        moving-average reference.

        If ADX is not provided, trend strength is
        reported as "Not Analyzed".
        """

        # ==========================================
        # Moving Average Selection
        # ==========================================

        moving_average = ema

        if moving_average is None:
            moving_average = sma

        # ==========================================
        # Trend Detection
        # ==========================================

        if moving_average is None:
            trend = "Neutral"

        elif current_price > moving_average:
            trend = "Bullish"

        elif current_price < moving_average:
            trend = "Bearish"

        else:
            trend = "Neutral"

        # ==========================================
        # Momentum Detection
        # ==========================================

        if rsi is None:
            momentum = "Unknown"

        elif rsi >= 70:
            momentum = "Overbought"

        elif rsi <= 30:
            momentum = "Oversold"

        elif rsi >= 50:
            momentum = "Positive"

        else:
            momentum = "Negative"

        # ==========================================
        # Volatility Detection
        # ==========================================

        if atr is None:
            volatility = "Unknown"

        elif atr > 0.002:
            volatility = "High"

        else:
            volatility = "Normal"

        # ==========================================
        # Trend Strength
        # ==========================================

        if adx is None:
            trend_strength = "Not Analyzed"

        elif adx >= 25:
            trend_strength = "Strong"

        elif adx >= 20:
            trend_strength = "Developing"

        else:
            trend_strength = "Weak"

        # ==========================================
        # Explanation
        # ==========================================

        explanation = (
            f"Price is {trend.lower()} with "
            f"{momentum.lower()} momentum and "
            f"{trend_strength.lower()} trend strength."
        )

        # ==========================================
        # Market Signal
        # ==========================================

        return MarketSignal(
            symbol=symbol,
            trend=trend,
            momentum=momentum,
            volatility=volatility,
            ema=(
                ema
                if ema is not None
                else moving_average
            ),
            rsi=rsi,
            atr=atr,
            adx=adx,
            explanation=explanation,
        )