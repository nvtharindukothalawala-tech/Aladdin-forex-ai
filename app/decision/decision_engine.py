"""
decision_engine.py

Contains DecisionEngine used by
the Aladdin Forex Trading Assistant.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.decision.decision_result import (
    DecisionResult,
)

from app.decision.decision_gate_result import (
    DecisionGateResult,
)


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
        Generate an intelligent trading decision.

        Complete market-structure analysis uses the
        detailed Decision Gate and returns DecisionGateResult.

        Older/simple market-intelligence results that do not
        contain complete structure confirmation continue to
        use the backward-compatible DecisionResult behaviour.
        """

        # ==========================================
        # Detect Complete Market Structure Analysis
        # ==========================================

        structure_direction = getattr(
            market_intelligence,
            "structure_direction",
            "NOT_ANALYZED",
        )

        structure_confirmation = getattr(
            market_intelligence,
            "structure_confirmation",
            "NOT_ANALYZED",
        )

        has_complete_structure = (
            structure_direction in {
                "BULLISH",
                "BEARISH",
            }
            and structure_confirmation in {
                "BOS_BULLISH",
                "BOS_BEARISH",
            }
        )

        # ==========================================
        # Decision Gate Path
        # ==========================================
        #
        # The Decision Gate is used when complete
        # market-structure information is available.
        #
        # This returns DecisionGateResult with:
        #
        # - action
        # - approved
        # - reason
        # - market_confidence
        # - timeframe_confidence
        # - decision_confidence
        # - gates_passed
        # - gates_failed
        #

        if has_complete_structure:

            return DecisionEngine.evaluate_gate(
                market_intelligence,
            )

        # ==========================================
        # Backward-Compatible Intelligent Decision
        # ==========================================

        action = "HOLD"

        confidence = (
            market_intelligence.confidence
        )

        reason = (
            "Market intelligence does not "
            "provide enough confirmation."
        )

        # ==========================================
        # Multi-Timeframe Decision Gate
        # ==========================================

        timeframe_alignment = (
            market_intelligence.timeframe_alignment
        )

        if timeframe_alignment in {
            "WEAK",
            "NONE",
        }:

            return DecisionResult(
                action="HOLD",
                confidence=confidence,
                reason=(
                    "Trade blocked because multi-timeframe "
                    "analysis is not aligned."
                ),
            )

        # ==========================================
        # Market Session Decision Gate
        # ==========================================

        if (
            market_intelligence.market_session
            != "NOT_ANALYZED"
            and market_intelligence.session_activity
            == "LOW"
        ):

            return DecisionResult(
                action="HOLD",
                confidence=confidence,
                reason=(
                    "Trade blocked because market session "
                    "activity is too low."
                ),
            )

        # ==========================================
        # Timeframe Confidence Adjustment
        # ==========================================

        if (
            timeframe_alignment
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
        # Session Confidence Adjustment
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

        # ==========================================
        # Confidence Gate
        # ==========================================

        if confidence < 70:

            return DecisionResult(
                action="HOLD",
                confidence=confidence,
                reason=(
                    "Trade held because adjusted decision "
                    "confidence is below 70%. "
                    f"Decision confidence: {confidence}%."
                ),
            )

        # ==========================================
        # BUY Decision
        # ==========================================

        if (
            market_intelligence.market_bias
            == "BULLISH"
            and market_intelligence.risk_level
            == "LOW"
            and confidence >= 70
        ):

            action = "BUY"

            if (
                timeframe_alignment
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
                        f"{timeframe_alignment}. "
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
                        f"{timeframe_alignment}. "
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
            market_intelligence.market_bias
            == "BEARISH"
            and market_intelligence.risk_level
            == "LOW"
            and confidence >= 70
        ):

            action = "SELL"

            if (
                timeframe_alignment
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
                        f"{timeframe_alignment}. "
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
                        f"{timeframe_alignment}. "
                        f"Decision confidence: {confidence}%."
                    )

            else:

                reason = (
                    "Bearish technical and news "
                    "intelligence confirms SELL opportunity."
                )

        # ==========================================
        # Final HOLD
        # ==========================================

        else:

            action = "HOLD"

            reason = (
                "Market intelligence does not "
                "provide enough confirmation."
            )

        # ==========================================
        # Backward-Compatible Result
        # ==========================================

        return DecisionResult(
            action=action,
            confidence=confidence,
            reason=reason,
        )

    @staticmethod
    def evaluate_gate(
        market_intelligence,
    ):
        """
        Evaluate all Decision Gate conditions.

        Returns a detailed DecisionGateResult
        explaining which gates passed or failed.
        """

        from app.decision.decision_gate_result import (
            DecisionGateResult,
        )

        # ==========================================
        # Confidence Values
        # ==========================================

        market_confidence = round(
            market_intelligence.confidence,
            2,
        )

        timeframe_confidence = round(
            market_intelligence.timeframe_confidence,
            2,
        )

        decision_confidence = (
            market_confidence
        )

        # ==========================================
        # Gate Tracking
        # ==========================================

        gates_passed = []
        gates_failed = []

        # ==========================================
        # Default Decision
        # ==========================================

        action = "HOLD"

        reason = (
            "Market intelligence does not "
            "provide enough confirmation."
        )

        # ==========================================
        # Gate 1: Multi-Timeframe Alignment
        # ==========================================

        timeframe_alignment = (
            market_intelligence.timeframe_alignment
        )

        if timeframe_alignment in {
            "FULL",
            "PARTIAL",
        }:

            gates_passed.append(
                "multi_timeframe_alignment"
            )

        elif timeframe_alignment in {
            "WEAK",
            "NONE",
        }:

            gates_failed.append(
                "multi_timeframe_alignment"
            )

            reason = (
                "Trade blocked because multi-timeframe "
                "analysis is not aligned."
            )

            return DecisionGateResult(
                action="HOLD",
                approved=False,
                reason=reason,
                market_confidence=market_confidence,
                timeframe_confidence=timeframe_confidence,
                decision_confidence=decision_confidence,
                gates_passed=gates_passed,
                gates_failed=gates_failed,
            )

        else:

            gates_failed.append(
                "multi_timeframe_alignment"
            )

            reason = (
                "Trade blocked because multi-timeframe "
                "analysis is unavailable."
            )

            return DecisionGateResult(
                action="HOLD",
                approved=False,
                reason=reason,
                market_confidence=market_confidence,
                timeframe_confidence=timeframe_confidence,
                decision_confidence=decision_confidence,
                gates_passed=gates_passed,
                gates_failed=gates_failed,
            )

        # ==========================================
        # Confidence Adjustment
        # ==========================================

        decision_confidence = (
            market_confidence * 0.70
            + timeframe_confidence * 0.30
        )

        decision_confidence = round(
            decision_confidence,
            2,
        )

        # ==========================================
        # Gate 2: Market Session
        # ==========================================

        if (
            market_intelligence.market_session
            != "NOT_ANALYZED"
            and market_intelligence.session_activity
            == "LOW"
        ):

            gates_failed.append(
                "market_session"
            )

            reason = (
                "Trade blocked because market session "
                "activity is too low."
            )

            return DecisionGateResult(
                action="HOLD",
                approved=False,
                reason=reason,
                market_confidence=market_confidence,
                timeframe_confidence=timeframe_confidence,
                decision_confidence=decision_confidence,
                gates_passed=gates_passed,
                gates_failed=gates_failed,
            )

        gates_passed.append(
            "market_session"
        )

        # ==========================================
        # Gate 3: Confidence
        # ==========================================

        if decision_confidence < 70:

            gates_failed.append(
                "confidence"
            )

            reason = (
                "Trade held because adjusted decision "
                "confidence is below 70%. "
                f"Decision confidence: "
                f"{decision_confidence}%."
            )

            return DecisionGateResult(
                action="HOLD",
                approved=False,
                reason=reason,
                market_confidence=market_confidence,
                timeframe_confidence=timeframe_confidence,
                decision_confidence=decision_confidence,
                gates_passed=gates_passed,
                gates_failed=gates_failed,
            )

        gates_passed.append(
            "confidence"
        )

        # ==========================================
        # Gate 4: Market Bias
        # ==========================================

        market_bias = (
            market_intelligence.market_bias
        )

        if market_bias not in {
            "BULLISH",
            "BEARISH",
        }:

            gates_failed.append(
                "market_bias"
            )

            reason = (
                "Trade held because market bias "
                "is neutral or unavailable."
            )

            return DecisionGateResult(
                action="HOLD",
                approved=False,
                reason=reason,
                market_confidence=market_confidence,
                timeframe_confidence=timeframe_confidence,
                decision_confidence=decision_confidence,
                gates_passed=gates_passed,
                gates_failed=gates_failed,
            )

        gates_passed.append(
            "market_bias"
        )

        # ==========================================
        # Gate 5: Market Structure Direction
        # ==========================================

        structure_direction = (
            market_intelligence.structure_direction
        )

        if (
            structure_direction
            != market_bias
        ):

            gates_failed.append(
                "market_structure_direction"
            )

            reason = (
                "Trade blocked because market structure "
                "does not confirm the market bias."
            )

            return DecisionGateResult(
                action="HOLD",
                approved=False,
                reason=reason,
                market_confidence=market_confidence,
                timeframe_confidence=timeframe_confidence,
                decision_confidence=decision_confidence,
                gates_passed=gates_passed,
                gates_failed=gates_failed,
            )

        gates_passed.append(
            "market_structure_direction"
        )

        # ==========================================
        # Gate 6: BOS Confirmation
        # ==========================================

        structure_confirmation = (
            market_intelligence.structure_confirmation
        )

        required_confirmation = (
            "BOS_BULLISH"
            if market_bias == "BULLISH"
            else "BOS_BEARISH"
        )

        if (
            structure_confirmation
            != required_confirmation
        ):

            gates_failed.append(
                "bos_confirmation"
            )

            reason = (
                f"Trade blocked because required "
                f"{required_confirmation} confirmation "
                "is unavailable."
            )

            return DecisionGateResult(
                action="HOLD",
                approved=False,
                reason=reason,
                market_confidence=market_confidence,
                timeframe_confidence=timeframe_confidence,
                decision_confidence=decision_confidence,
                gates_passed=gates_passed,
                gates_failed=gates_failed,
            )

        gates_passed.append(
            "bos_confirmation"
        )

        # ==========================================
        # Gate 7: Risk Level
        # ==========================================

        if (
            market_intelligence.risk_level
            != "LOW"
        ):

            gates_failed.append(
                "risk_level"
            )

            reason = (
                "Trade blocked because risk level is "
                f"{market_intelligence.risk_level}."
            )

            return DecisionGateResult(
                action="HOLD",
                approved=False,
                reason=reason,
                market_confidence=market_confidence,
                timeframe_confidence=timeframe_confidence,
                decision_confidence=decision_confidence,
                gates_passed=gates_passed,
                gates_failed=gates_failed,
            )

        gates_passed.append(
            "risk_level"
        )

        # ==========================================
        # Gate 8: Session Opportunity Bonus
        # ==========================================

        if (
            market_intelligence.market_session
            != "NOT_ANALYZED"
            and market_intelligence.session_condition
            == "HIGH_OPPORTUNITY"
        ):

            decision_confidence += 5.0

            decision_confidence = min(
                decision_confidence,
                100.0,
            )

            decision_confidence = round(
                decision_confidence,
                2,
            )

            gates_passed.append(
                "high_opportunity_session"
            )

        # ==========================================
        # Final Decision
        # ==========================================

        if market_bias == "BULLISH":

            action = "BUY"

        else:

            action = "SELL"

        reason = (
            f"{action} approved by the Decision Gate. "
            f"Market bias: {market_bias}. "
            f"Structure confirmation: "
            f"{structure_confirmation}. "
            f"MTF alignment: "
            f"{timeframe_alignment}. "
            f"Decision confidence: "
            f"{decision_confidence}%."
        )

        # ==========================================
        # Return Approved Result
        # ==========================================

        return DecisionGateResult(
            action=action,
            approved=True,
            reason=reason,
            market_confidence=market_confidence,
            timeframe_confidence=timeframe_confidence,
            decision_confidence=decision_confidence,
            gates_passed=gates_passed,
            gates_failed=gates_failed,
        )