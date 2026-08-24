"""
market_structure_agent.py

Market Structure Intelligence Agent.

Author: Tharindu Kothalawala
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
        bos=None,
        choch=None,
        liquidity_sweep_details=None,
        order_block_details=None,
        fvg_details=None,
        swing_highs=None,
        swing_lows=None,
    ):
        """
        Generate market structure analysis.

        The original simple inputs are kept for
        backward compatibility.

        Detailed SMC event data can also be supplied.
        """

        signals = []

        confidence = 50

        # ==========================================
        # Structure Detection
        # ==========================================

        if price_structure == "BOS_BULLISH":

            structure = "BOS"

            trend_direction = "BULLISH"

            confidence += 15

            signals.append(
                "Bullish break of structure detected"
            )

        elif price_structure == "BOS_BEARISH":

            structure = "BOS"

            trend_direction = "BEARISH"

            confidence += 15

            signals.append(
                "Bearish break of structure detected"
            )

        elif price_structure == "CHOCH":

            structure = "CHoCH"

            trend_direction = "REVERSAL"

            confidence += 10

            signals.append(
                "Change of character detected"
            )

        else:

            structure = "RANGE"

            trend_direction = "NEUTRAL"

        # ==========================================
        # Detailed BOS
        # ==========================================

        if bos is not None:

            bos_type = bos.get("type")

            if bos_type == "BOS_BULLISH":

                signals.append(
                    "Detailed bullish BOS confirmed"
                )

            elif bos_type == "BOS_BEARISH":

                signals.append(
                    "Detailed bearish BOS confirmed"
                )

        # ==========================================
        # CHoCH
        # ==========================================

        if choch is not None:

            choch_type = choch.get("type")

            if choch_type == "CHOCH_BULLISH":

                signals.append(
                    "Bullish change of character detected"
                )

                confidence += 5

            elif choch_type == "CHOCH_BEARISH":

                signals.append(
                    "Bearish change of character detected"
                )

                confidence += 5

        # ==========================================
        # Liquidity Analysis
        # ==========================================

        if liquidity_sweep:

            liquidity_status = "SWEEP_COMPLETED"

            confidence += 10

            signals.append(
                "Liquidity sweep detected"
            )

        else:

            liquidity_status = "NO_SWEEP"

        # ==========================================
        # Detailed Liquidity Sweep
        # ==========================================

        if liquidity_sweep_details is not None:

            sweep_type = liquidity_sweep_details.get(
                "type"
            )

            if sweep_type == "LIQUIDITY_SWEEP_HIGH":

                signals.append(
                    "High-side liquidity sweep detected"
                )

            elif sweep_type == "LIQUIDITY_SWEEP_LOW":

                signals.append(
                    "Low-side liquidity sweep detected"
                )

        # ==========================================
        # Order Block
        # ==========================================

        if order_block == "BULLISH":

            signals.append(
                "Bullish order block identified"
            )

            confidence += 5

        elif order_block == "BEARISH":

            signals.append(
                "Bearish order block identified"
            )

            confidence += 5

        # ==========================================
        # Detailed Order Block
        # ==========================================

        if order_block_details is not None:

            order_block_type = order_block_details.get(
                "type"
            )

            if order_block_type == "ORDER_BLOCK_BULLISH":

                signals.append(
                    "Detailed bullish order block confirmed"
                )

            elif order_block_type == "ORDER_BLOCK_BEARISH":

                signals.append(
                    "Detailed bearish order block confirmed"
                )

        # ==========================================
        # Fair Value Gap
        # ==========================================

        if fair_value_gap:

            signals.append(
                "Fair value gap detected"
            )

            confidence += 5

        # ==========================================
        # Detailed FVG
        # ==========================================

        if fvg_details is not None:

            fvg_type = fvg_details.get(
                "type"
            )

            if fvg_type == "FVG_BULLISH":

                signals.append(
                    "Bullish fair value gap confirmed"
                )

            elif fvg_type == "FVG_BEARISH":

                signals.append(
                    "Bearish fair value gap confirmed"
                )

        # ==========================================
        # Swing Information
        # ==========================================

        if swing_highs:

            signals.append(
                f"{len(swing_highs)} swing highs identified"
            )

        if swing_lows:

            signals.append(
                f"{len(swing_lows)} swing lows identified"
            )

        # ==========================================
        # Final Result
        # ==========================================

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
            bos=bos,
            choch=choch,
            liquidity_sweep=liquidity_sweep_details,
            order_block_details=order_block_details,
            fvg_details=fvg_details,
            swing_highs=swing_highs,
            swing_lows=swing_lows,
        )