"""
decision_routes.py

Contains API endpoints for
trading decision generation.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi import APIRouter


from app.decision.decision_engine import (
    DecisionEngine,
)

from app.schemas.decision_schema import (
    DecisionRequest,
)

router = APIRouter(
    prefix="/decision",
    tags=["Decision Engine"],
)


@router.post("/analyze")
def analyze_decision(
    data: DecisionRequest,
):
    """
    Generate trading decision.
    """

    result = DecisionEngine.make_decision(
        trend=data.trend,
        momentum=data.momentum,
        risk_reward=data.risk_reward,
    )

    return result
