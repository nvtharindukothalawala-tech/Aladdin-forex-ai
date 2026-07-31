"""
market_intelligence.py

Combines technical, news,
and market structure analysis.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.intelligence.market_result import (
    MarketIntelligenceResult,
)


class MarketIntelligenceAgent:
    """
    Combines multiple intelligence sources.
    """

    @staticmethod
    def analyze(
        technical_result,
        news_result,
        structure_result,
    ):
        """
        Generate advanced market intelligence.
        """

        confidence = (
            technical_result.confidence
            + news_result.confidence
            + structure_result.confidence
        ) / 3

        # Determine market bias

        bullish_signals = 0

        bearish_signals = 0

        if technical_result.trend == "BULLISH":

            bullish_signals += 1

        elif technical_result.trend == "BEARISH":

            bearish_signals += 1

        if news_result.sentiment == "BULLISH":

            bullish_signals += 1

        elif news_result.sentiment == "BEARISH":

            bearish_signals += 1

        if structure_result.trend_direction == "BULLISH":

            bullish_signals += 1

        elif structure_result.trend_direction == "BEARISH":

            bearish_signals += 1

        if bullish_signals >= 2:

            market_bias = "BULLISH"

            recommendation = "Consider BUY opportunities"

        elif bearish_signals >= 2:

            market_bias = "BEARISH"

            recommendation = "Consider SELL opportunities"

        else:

            market_bias = "NEUTRAL"

            recommendation = "Wait for stronger confirmation"

        # Risk level

        if confidence >= 80:

            risk_level = "LOW"

        elif confidence >= 60:

            risk_level = "MEDIUM"

        else:

            risk_level = "HIGH"

        return MarketIntelligenceResult(
            market_bias=market_bias,
            confidence=round(
                confidence,
                2,
            ),
            technical_summary=(
                f"Trend: {technical_result.trend}, "
                f"Momentum: {technical_result.momentum}"
            ),
            news_summary=(
                f"{news_result.currency} " f"sentiment: {news_result.sentiment}"
            ),
            structure_summary=(
                f"{structure_result.structure}, "
                f"{structure_result.trend_direction}, "
                f"Liquidity: "
                f"{structure_result.liquidity_status}"
            ),
            risk_level=risk_level,
            recommendation=recommendation,
        )
