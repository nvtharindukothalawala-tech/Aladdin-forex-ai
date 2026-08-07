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

        # ==========================================
        # Weighted Confidence Calculation
        # ==========================================

        technical_weight = 0.40
        structure_weight = 0.40
        news_weight = 0.20

        confidence = (
            technical_result.confidence * technical_weight
            + structure_result.confidence * structure_weight
            + news_result.confidence * news_weight
        )

        confidence_summary = (
            f"Technical: {technical_result.confidence:g} x 40%, "
            f"Structure: {structure_result.confidence:g} x 40%, "
            f"News: {news_result.confidence:g} x 20%, "
            f"Final confidence: {round(confidence, 2)}%"
        )

        # ==========================================
        # Determine Market Bias
        # ==========================================

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

        # ==========================================
        # Detect Agent Conflict
        # ==========================================

        conflict_detected = False

        conflict_summary = (
            "No significant agent conflict detected"
        )

        technical_direction = technical_result.trend
        news_direction = news_result.sentiment
        structure_direction = (
            structure_result.trend_direction
        )

        if (
            technical_direction == structure_direction
            and news_direction != technical_direction
            and news_direction in {"BULLISH", "BEARISH"}
        ):
            conflict_detected = True

            conflict_summary = (
                "News analysis disagrees with technical "
                "and market structure analysis"
            )

        elif (
            technical_direction == news_direction
            and structure_direction != technical_direction
            and structure_direction in {"BULLISH", "BEARISH"}
        ):
            conflict_detected = True

            conflict_summary = (
                "Market structure analysis disagrees with "
                "technical and news analysis"
            )

        elif (
            news_direction == structure_direction
            and technical_direction != news_direction
            and technical_direction in {"BULLISH", "BEARISH"}
        ):
            conflict_detected = True

            conflict_summary = (
                "Technical analysis disagrees with news "
                "and market structure analysis"
            )

        # ==========================================
        # Determine Risk Level
        # ==========================================

        if confidence >= 80:
            risk_level = "LOW"

        elif confidence >= 60:
            risk_level = "MEDIUM"

        else:
            risk_level = "HIGH"


        # ==========================================
        # Increase Risk When Agents Disagree
        # ==========================================

        if conflict_detected:

            if risk_level == "LOW":
                risk_level = "MEDIUM"

            elif risk_level == "MEDIUM":
                risk_level = "HIGH"
        # ==========================================
        # Return Combined Result
        # ==========================================

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
                f"{news_result.currency} "
                f"sentiment: {news_result.sentiment}"
            ),
            structure_summary=(
                f"{structure_result.structure}, "
                f"{structure_result.trend_direction}, "
                f"Liquidity: "
                f"{structure_result.liquidity_status}"
            ),
            risk_level=risk_level,
            recommendation=recommendation,
            conflict_detected=conflict_detected,
            conflict_summary=conflict_summary,
            confidence_summary=confidence_summary,
        )