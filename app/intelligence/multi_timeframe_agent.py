"""
multi_timeframe_agent.py

Multi-Timeframe Analysis Agent for Aladdin.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.intelligence.multi_timeframe_result import (
    MultiTimeframeResult,
)


class MultiTimeframeAgent:
    """
    Compares market direction across multiple timeframes.
    """

    @staticmethod
    def analyze(
        higher_timeframe_bias,
        middle_timeframe_bias,
        entry_timeframe_bias,
    ):
        """
        Analyze alignment between higher,
        middle, and entry timeframes.
        """

        # ==========================================
        # Full Alignment
        # ==========================================

        if (
            higher_timeframe_bias
            == middle_timeframe_bias
            == entry_timeframe_bias
        ):
            alignment = "FULL"

            confidence = 100.0

            summary = (
                "All monitored timeframes are aligned "
                f"{higher_timeframe_bias}"
            )

        # ==========================================
        # Partial Alignment
        # ==========================================

        elif (
            higher_timeframe_bias
            == middle_timeframe_bias
        ):
            alignment = "PARTIAL"

            confidence = 75.0

            summary = (
                "Higher and middle timeframes agree, "
                "but entry timeframe differs"
            )

        # ==========================================
        # Weak Alignment
        # ==========================================

        elif (
            middle_timeframe_bias
            == entry_timeframe_bias
        ):
            alignment = "WEAK"

            confidence = 60.0

            summary = (
                "Middle and entry timeframes agree, "
                "but higher timeframe differs"
            )

        # ==========================================
        # No Alignment
        # ==========================================

        else:
            alignment = "NONE"

            confidence = 40.0

            summary = (
                "Timeframes are not aligned"
            )

        return MultiTimeframeResult(
            higher_timeframe_bias=higher_timeframe_bias,
            middle_timeframe_bias=middle_timeframe_bias,
            entry_timeframe_bias=entry_timeframe_bias,
            alignment=alignment,
            confidence=confidence,
            summary=summary,
        )