"""
reasoning_engine.py

Creates explainable AI trade reasoning.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from app.intelligence.reasoning_result import (
    TradeReasonResult,
)


class ReasoningEngine:
    """
    Converts analysis results into
    human-readable trade reasoning.
    """

    @staticmethod
    def generate(
        decision,
        confidence,
        ema_signal,
        rsi_value,
        adx_value,
        price_structure,
        liquidity_sweep,
        risk_approved,
    ):

        technical = []

        structure = []

        risk = []


        # Technical reasoning

        if ema_signal == "BULLISH":

            technical.append(
                "EMA trend confirms bullish momentum."
            )

        elif ema_signal == "BEARISH":

            technical.append(
                "EMA trend confirms bearish momentum."
            )


        if rsi_value >= 60:

            technical.append(
                "RSI confirms buying momentum."
            )

        elif rsi_value <= 40:

            technical.append(
                "RSI confirms selling pressure."
            )


        if adx_value >= 25:

            technical.append(
                "ADX confirms strong trend strength."
            )


        # Structure reasoning

        structure.append(
            f"Market structure: {price_structure}"
        )


        if liquidity_sweep:

            structure.append(
                "Liquidity sweep detected."
            )


        # Risk reasoning

        if risk_approved:

            risk.append(
                "Risk validation passed."
            )

        else:

            risk.append(
                "Risk validation failed."
            )


        message = (
            f"{decision} decision generated "
            "based on technical, structure "
            "and risk analysis."
        )


        return TradeReasonResult(
            decision=decision,
            confidence=confidence,
            technical_reasons=technical,
            structure_reasons=structure,
            risk_reasons=risk,
            final_message=message,
        )