"""
market_structure_agent.py

Market Structure Intelligence Agent.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.intelligence.market_structure_result import (
    MarketStructureResult,
)


class MarketStructureAgent:
    """
    Analyzes Smart Money Concepts.

    Includes:

    - Break of Structure (BOS)
    - Change of Character (CHoCH)
    - Liquidity
    - Order Blocks
    - Fair Value Gap
    """

    @staticmethod
    def analyze(
        price_structure,
        liquidity_sweep,
        order_block,
        fair_value_gap,
    ):
        """
        Generate market structure analysis.
        """

        signals = []

        confidence = 50

        # Structure detection

        if price_structure == "BOS_BULLISH":

            structure = "BOS"

            trend_direction = "BULLISH"

            confidence += 15

            signals.append("Bullish break of structure detected")

        elif price_structure == "BOS_BEARISH":

            structure = "BOS"

            trend_direction = "BEARISH"

            confidence += 15

            signals.append("Bearish break of structure detected")

        elif price_structure == "CHOCH":

            structure = "CHoCH"

            trend_direction = "REVERSAL"

            confidence += 10

            signals.append("Change of character detected")

        else:

            structure = "RANGE"

            trend_direction = "NEUTRAL"

        # Liquidity analysis

        if liquidity_sweep:

            liquidity_status = "SWEEP_COMPLETED"

            confidence += 10

            signals.append("Liquidity sweep detected")

        else:

            liquidity_status = "NO_SWEEP"

        # Order block

        if order_block == "BULLISH":

            signals.append("Bullish order block identified")

            confidence += 5

        elif order_block == "BEARISH":

            signals.append("Bearish order block identified")

            confidence += 5

        # Fair Value Gap

        if fair_value_gap:

            signals.append("Fair value gap detected")

            confidence += 5

        return MarketStructureResult(
            structure=structure,
            trend_direction=trend_direction,
            liquidity_status=liquidity_status,
            order_block=order_block,
            fair_value_gap=fair_value_gap,
            confidence=min(
                confidence,
                100,
            ),
            signals=signals,
        )
