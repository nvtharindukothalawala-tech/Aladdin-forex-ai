"""
technical_agent.py

Technical Analysis Agent for Aladdin.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.intelligence.technical_result import (
    TechnicalAnalysisResult,
)


class TechnicalAgent:
    """
    Analyzes technical market conditions.
    """

    @staticmethod
    def analyze(
        ema_signal,
        rsi_value,
        adx_value,
        volatility,
    ):
        """
        Generate technical analysis result.
        """

        signals = []

        confidence = 50

        # Trend analysis

        if ema_signal == "BULLISH":

            trend = "BULLISH"

            confidence += 15

            signals.append("EMA confirms bullish trend")

        elif ema_signal == "BEARISH":

            trend = "BEARISH"

            confidence += 15

            signals.append("EMA confirms bearish trend")

        else:

            trend = "NEUTRAL"

        # Momentum analysis

        if rsi_value >= 60:

            momentum = "STRONG"

            confidence += 10

            signals.append("RSI shows positive momentum")

        elif rsi_value <= 40:

            momentum = "WEAK"

            signals.append("RSI shows weak momentum")

        else:

            momentum = "NORMAL"

        # Trend strength

        if adx_value >= 25:

            confidence += 10

            signals.append("ADX confirms strong trend")

        return TechnicalAnalysisResult(
            trend=trend,
            momentum=momentum,
            volatility=volatility,
            confidence=min(
                confidence,
                100,
            ),
            signals=signals,
        )
