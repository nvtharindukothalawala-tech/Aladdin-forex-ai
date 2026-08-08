"""
market_result.py

Stores combined market intelligence results.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from dataclasses import dataclass


@dataclass
class MarketIntelligenceResult:
    """
    Combined output from AI agents.

    Supports:
    - Technical Agent
    - News Agent
    - Market Structure Agent
    """

    market_bias: str

    confidence: float

    technical_summary: str

    news_summary: str

    structure_summary: str = (
        "No market structure analysis available"
    )

    risk_level: str = (
        "UNKNOWN"
    )

    recommendation: str = (
        "Wait for stronger confirmation"
    )

    conflict_detected: bool = False

    conflict_summary: str = (
        "No significant agent conflict detected"
    )

    confidence_summary: str = (
        "Confidence explanation not available"
    )

    timeframe_alignment: str = "NOT_ANALYZED"

    timeframe_confidence: float = 0.0

    timeframe_summary: str = (
        "Multi-timeframe analysis not available"
    )

    market_session: str = "NOT_ANALYZED"

    session_activity: str = "UNKNOWN"

    session_condition: str = "UNKNOWN"

    session_summary: str = (
        "Market session analysis not available"
    )