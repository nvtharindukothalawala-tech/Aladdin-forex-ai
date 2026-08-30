"""
ai_trade_reason.py

Generates human-readable explanations
for AI trading decisions.

Author: Tharindu Kothalawala
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

        technical_reason = (
            market_intelligence.technical_summary
        )

        news_reason = (
            market_intelligence.news_summary
        )

        structure_reason = (
            market_intelligence.structure_summary
        )

        risk_reason = risk_validation.reason

        # ==========================================
        # Multi-Timeframe Reasoning
        # ==========================================

        timeframe_alignment = (
            market_intelligence.timeframe_alignment
        )

        timeframe_summary = (
            market_intelligence.timeframe_summary
        )

        if timeframe_alignment == "FULL":

            timeframe_reason = (
                f"{timeframe_summary}. "
                "Multi-timeframe confirmation supports "
                "the decision."
            )

        elif timeframe_alignment == "PARTIAL":

            timeframe_reason = (
                f"{timeframe_summary}. "
                "Multi-timeframe confirmation is only "
                "partial."
            )

        elif timeframe_alignment == "NONE":

            timeframe_reason = (
                f"{timeframe_summary}. "
                "Multi-timeframe confirmation is absent."
            )

        else:

            timeframe_reason = (
                f"{timeframe_summary}."
            )

        # ==========================================
        # Market Session Reasoning
        # ==========================================

        session_activity = (
            market_intelligence.session_activity
        )

        session_condition = (
            market_intelligence.session_condition
        )

        session_summary = (
            market_intelligence.session_summary
        )

        if session_condition == "HIGH_OPPORTUNITY":

            session_reason = (
                f"{session_summary}. "
                "The current market session provides "
                "a high-opportunity trading environment."
            )

        elif session_activity == "LOW":

            session_reason = (
                f"{session_summary}. "
                "Low market activity reduces the quality "
                "of the trading opportunity."
            )

        else:

            session_reason = (
                f"{session_summary}."
            )

        # ==========================================
        # Decision Gate Reasoning
        # ==========================================

        gates_passed = list(
            getattr(
                decision,
                "gates_passed",
                [],
            )
        )

        gates_failed = list(
            getattr(
                decision,
                "gates_failed",
                [],
            )
        )

        gate_reason = getattr(
            decision,
            "reason",
            "Decision Gate information not available.",
        )

        # ==========================================
        # Final Reason
        # ==========================================

        final_reason = (
            "Decision generated using "
            "technical analysis, news sentiment, "
            "market structure, multi-timeframe analysis, "
            "market session analysis, Decision Gate "
            "validation, and risk validation."
        )

        return AIReasonResult(
            decision=decision.action,
            confidence=(
                getattr(
                    decision,
                    "decision_confidence",
                    market_intelligence.confidence,
                )
            ),
            technical_reason=technical_reason,
            news_reason=news_reason,
            structure_reason=structure_reason,
            risk_reason=risk_reason,
            final_reason=final_reason,
            timeframe_reason=timeframe_reason,
            session_reason=session_reason,
            gate_reason=gate_reason,
            gates_passed=gates_passed,
            gates_failed=gates_failed,
        )