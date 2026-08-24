"""
decision_gate_schema.py

Pydantic response schemas for
Aladdin Decision Gate API.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from pydantic import BaseModel


class DecisionGateResponse(BaseModel):
    """
    Final Decision Gate response.
    """

    action: str

    approved: bool

    market_confidence: float

    timeframe_confidence: float

    decision_confidence: float

    reason: str

    gates_passed: list[str]

    gates_failed: list[str]


class MarketIntelligenceResponse(BaseModel):
    """
    Market intelligence information returned
    together with the final decision.
    """

    market_bias: str

    confidence: float

    risk_level: str

    recommendation: str

    structure_direction: str

    structure_confirmation: str

    timeframe_alignment: str

    timeframe_confidence: float

    timeframe_summary: str

    market_session: str

    session_activity: str

    session_condition: str

    session_summary: str

    technical_summary: str

    news_summary: str

    structure_summary: str

    conflict_detected: bool

    conflict_summary: str

    confidence_summary: str


class IntelligentDecisionResponse(BaseModel):
    """
    Complete response from the live
    intelligent decision endpoint.
    """

    symbol: str

    decision: DecisionGateResponse

    market_intelligence: MarketIntelligenceResponse