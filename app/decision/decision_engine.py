"""
decision_engine.py

Contains DecisionEngine used by
the Aladdin Forex Trading Assistant.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.decision.decision_result import DecisionResult


class DecisionEngine:
    """
    Generate trading decisions based on
    market analysis.
    """

    @staticmethod
    def make_decision(
        trend,
        momentum,
        risk_reward,
    ):
        """
        Generate BUY, SELL, or HOLD decision.

        Rules:

        BUY:
            Bullish trend
            Positive momentum
            Risk reward >= 2

        SELL:
            Bearish trend
            Negative momentum
            Risk reward >= 2

        Otherwise:
            HOLD
        """

        action = "HOLD"

        confidence = 50

        reason = "Market conditions are not strong enough."

        if trend == "Bullish" and momentum == "Positive" and risk_reward >= 2:

            action = "BUY"

            confidence = 75

            reason = (
                "Bullish trend with positive momentum " "and acceptable risk reward."
            )

        elif trend == "Bearish" and momentum == "Negative" and risk_reward >= 2:

            action = "SELL"

            confidence = 75

            reason = (
                "Bearish trend with negative momentum " "and acceptable risk reward."
            )

        return DecisionResult(
            action=action,
            confidence=confidence,
            reason=reason,
        )

    @staticmethod
    def make_intelligent_decision(
        market_intelligence,
    ):
        """
        Generate trading decision
        using AI market intelligence.
        """

        action = "HOLD"

        confidence = market_intelligence.confidence

        reason = "Market intelligence does not " "provide enough confirmation."

        if (
            market_intelligence.market_bias == "BULLISH"
            and market_intelligence.risk_level == "LOW"
            and market_intelligence.confidence >= 70
        ):

            action = "BUY"

            reason = (
                "Bullish technical and news " "intelligence confirms BUY opportunity."
            )

        elif (
            market_intelligence.market_bias == "BEARISH"
            and market_intelligence.risk_level == "LOW"
            and market_intelligence.confidence >= 70
        ):

            action = "SELL"

            reason = (
                "Bearish technical and news " "intelligence confirms SELL opportunity."
            )

        return DecisionResult(
            action=action,
            confidence=confidence,
            reason=reason,
        )
