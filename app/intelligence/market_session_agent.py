"""
market_session_agent.py

Forex Market Session Intelligence Agent.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.intelligence.market_session_result import (
    MarketSessionResult,
)


class MarketSessionAgent:
    """
    Analyzes the active Forex trading session
    using UTC time.
    """

    @staticmethod
    def analyze(
        hour_utc,
    ):
        """
        Determine the Forex market session.

        Current simplified UTC rules:

        Asian:
            00:00 - 07:59 UTC

        London:
            08:00 - 12:59 UTC

        London/New York Overlap:
            13:00 - 15:59 UTC

        New York:
            16:00 - 20:59 UTC

        Other:
            21:00 - 23:59 UTC
        """

        # ==========================================
        # Validate UTC Hour
        # ==========================================

        if not isinstance(hour_utc, int):
            raise ValueError(
                "hour_utc must be an integer between 0 and 23"
            )

        if hour_utc < 0 or hour_utc > 23:
            raise ValueError(
                "hour_utc must be between 0 and 23"
            )

        # ==========================================
        # Asian Session
        # ==========================================

        if 0 <= hour_utc < 8:
            session = "ASIAN"

            activity_level = "MEDIUM"

            trading_condition = "NORMAL"

            summary = (
                "Asian session is active with "
                "moderate market activity."
            )

        # ==========================================
        # London Session
        # ==========================================

        elif 8 <= hour_utc < 13:
            session = "LONDON"

            activity_level = "HIGH"

            trading_condition = "FAVORABLE"

            summary = (
                "London session is active with "
                "high market activity."
            )

        # ==========================================
        # London / New York Overlap
        # ==========================================

        elif 13 <= hour_utc < 16:
            session = "LONDON_NEW_YORK_OVERLAP"

            activity_level = "VERY_HIGH"

            trading_condition = "HIGH_OPPORTUNITY"

            summary = (
                "London and New York sessions overlap "
                "with very high market activity."
            )

        # ==========================================
        # New York Session
        # ==========================================

        elif 16 <= hour_utc < 21:
            session = "NEW_YORK"

            activity_level = "HIGH"

            trading_condition = "FAVORABLE"

            summary = (
                "New York session is active with "
                "high market activity."
            )

        # ==========================================
        # Other Market Period
        # ==========================================

        else:
            session = "OTHER"

            activity_level = "LOW"

            trading_condition = "NEUTRAL"

            summary = (
                "Major Forex trading sessions "
                "are currently less active."
            )

        # ==========================================
        # Return Session Result
        # ==========================================

        return MarketSessionResult(
            session=session,
            activity_level=activity_level,
            trading_condition=trading_condition,
            summary=summary,
        )