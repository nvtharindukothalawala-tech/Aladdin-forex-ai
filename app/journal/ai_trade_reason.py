"""
ai_trade_reason.py

Generates human-readable explanations
for AI trading decisions.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.journal.ai_reason_result import (
    AIReasonResult,
)


class AITradeReasonGenerator:
    """
    Creates explanations for AI decisions.
    """

    @staticmethod
    def generate(
        decision,
        market_intelligence,
        risk_validation,
    ):
        """
        Generate AI trade explanation.
        """

        technical_reason = market_intelligence.technical_summary

        news_reason = market_intelligence.news_summary

        structure_reason = market_intelligence.structure_summary

        if risk_validation.approved:

            risk_reason = "Trade risk is within allowed limit."

        else:

            risk_reason = "Trade risk exceeds maximum allowed risk."

        final_reason = (
            "Decision generated using "
            "technical analysis, news sentiment, "
            "market structure, and risk validation."
        )

        return AIReasonResult(
            decision=decision.action,
            confidence=market_intelligence.confidence,
            technical_reason=technical_reason,
            news_reason=news_reason,
            structure_reason=structure_reason,
            risk_reason=risk_reason,
            final_reason=final_reason,
        )
