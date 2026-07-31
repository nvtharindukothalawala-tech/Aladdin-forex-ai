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