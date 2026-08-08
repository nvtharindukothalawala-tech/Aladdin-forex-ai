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

        if (
            trend == "Bullish"
            and momentum == "Positive"
            and risk_reward >= 2
        ):
            action = "BUY"
            confidence = 75

            reason = (
                "Bullish trend with positive momentum "
                "and acceptable risk reward."
            )

        elif (
            trend == "Bearish"
            and momentum == "Negative"
            and risk_reward >= 2
        ):
            action = "SELL"
            confidence = 75

            reason = (
                "Bearish trend with negative momentum "
                "and acceptable risk reward."
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

        Multi-timeframe rules:

        - FULL: Trading decision may continue.
        - PARTIAL: Trading decision may continue.
        - WEAK: Block trade and HOLD.
        - NONE: Block trade and HOLD.
        - NOT_ANALYZED: Keep backward compatibility.
        """

        action = "HOLD"

        confidence = market_intelligence.confidence

        reason = (
            "Market intelligence does not "
            "provide enough confirmation."
        )

        # ==========================================
        # Multi-Timeframe Decision Gate
        # ==========================================

        blocked_timeframe_alignments = {
            "WEAK",
            "NONE",
        }

        if (
            market_intelligence.timeframe_alignment
            in blocked_timeframe_alignments
        ):
            reason = (
                "Trade blocked because multi-timeframe "
                "analysis is not aligned."
            )

            return DecisionResult(
                action=action,
                confidence=confidence,
                reason=reason,
            )

        # ==========================================
        # Market Session Decision Gate
        # ==========================================

        if (
            market_intelligence.market_session != "NOT_ANALYZED"
            and market_intelligence.session_activity == "LOW"
        ):
            reason = (
                "Trade blocked because market session "
                "activity is too low."
            )

            return DecisionResult(
                action="HOLD",
                confidence=confidence,
                reason=reason,
            )

        # ==========================================
        # Timeframe-Aware Confidence Adjustment
        # ==========================================

        if (
            market_intelligence.timeframe_alignment
            != "NOT_ANALYZED"
        ):
            market_weight = 0.70
            timeframe_weight = 0.30

            confidence = (
                market_intelligence.confidence
                * market_weight
                + market_intelligence.timeframe_confidence
                * timeframe_weight
            )

            confidence = round(
                confidence,
                2,
            )

        # ==========================================
        # Session-Aware Confidence Adjustment
        # ==========================================

        if (
            market_intelligence.market_session
            != "NOT_ANALYZED"
            and market_intelligence.session_condition
            == "HIGH_OPPORTUNITY"
        ):
            session_bonus = 5.0

            confidence += session_bonus

            confidence = min(
                confidence,
                100.0,
            )

            confidence = round(
                confidence,
                2,
            )

        if confidence < 70:
            reason = (
                "Trade held because adjusted decision "
                "confidence is below 70%. "
                f"Decision confidence: {confidence}%."
            )

        # ==========================================
        # BUY Decision
        # ==========================================

        if (
            market_intelligence.market_bias == "BULLISH"
            and market_intelligence.risk_level == "LOW"
            and confidence >= 70
        ):
            action = "BUY"

            if (
                market_intelligence.timeframe_alignment
                != "NOT_ANALYZED"
            ):
                if (
                    market_intelligence.market_session
                    != "NOT_ANALYZED"
                    and market_intelligence.session_condition
                    == "HIGH_OPPORTUNITY"
                ):
                    reason = (
                        "Bullish market intelligence supports BUY. "
                        f"Timeframe alignment: "
                        f"{market_intelligence.timeframe_alignment}. "
                        f"Market session: "
                        f"{market_intelligence.market_session}. "
                        f"Session condition: "
                        f"{market_intelligence.session_condition}. "
                        f"Decision confidence: {confidence}%."
                    )

                else:
                    reason = (
                        "Bullish market intelligence supports BUY. "
                        f"Timeframe alignment: "
                        f"{market_intelligence.timeframe_alignment}. "
                        f"Decision confidence: {confidence}%."
                    )

            else:
                reason = (
                    "Bullish technical and news "
                    "intelligence confirms BUY opportunity."
                )

        # ==========================================
        # SELL Decision
        # ==========================================

        elif (
            market_intelligence.market_bias == "BEARISH"
            and market_intelligence.risk_level == "LOW"
            and confidence >= 70
        ):
            action = "SELL"

            if (
                market_intelligence.timeframe_alignment
                != "NOT_ANALYZED"
            ):
                if (
                    market_intelligence.market_session
                    != "NOT_ANALYZED"
                    and market_intelligence.session_condition
                    == "HIGH_OPPORTUNITY"
                ):
                    reason = (
                        "Bearish market intelligence supports SELL. "
                        f"Timeframe alignment: "
                        f"{market_intelligence.timeframe_alignment}. "
                        f"Market session: "
                        f"{market_intelligence.market_session}. "
                        f"Session condition: "
                        f"{market_intelligence.session_condition}. "
                        f"Decision confidence: {confidence}%."
                    )

                else:
                    reason = (
                        "Bearish market intelligence supports SELL. "
                        f"Timeframe alignment: "
                        f"{market_intelligence.timeframe_alignment}. "
                        f"Decision confidence: {confidence}%."
                    )

            else:
                reason = (
                    "Bearish technical and news "
                    "intelligence confirms SELL opportunity."
                )

        return DecisionResult(
            action=action,
            confidence=confidence,
            reason=reason,
        )