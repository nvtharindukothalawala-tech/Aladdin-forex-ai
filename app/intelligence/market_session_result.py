"""
market_session_result.py

Stores Forex market session analysis results.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from dataclasses import dataclass


@dataclass
class MarketSessionResult:
    """
    Represents Forex market session analysis.
    """

    session: str

    activity_level: str

    trading_condition: str

    summary: str