"""
decision_routes.py

Contains API endpoints for
trading decision generation.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi import APIRouter, HTTPException

from app.decision.decision_engine import (
    DecisionEngine,
)

from app.schemas.decision_schema import (
    DecisionRequest,
)

from app.schemas.decision_gate_schema import (
    IntelligentDecisionResponse,
)

from app.services.market_intelligence_service import (
    MarketIntelligenceService,
)


router = APIRouter(
    prefix="/decision",
    tags=["Decision Engine"],
)


# ==========================================
# Existing Basic Decision API
# ==========================================


@router.post("/analyze")
def analyze_decision(
    data: DecisionRequest,
):
    """
    Generate a basic trading decision.
    """

    result = DecisionEngine.make_decision(
        trend=data.trend,
        momentum=data.momentum,
        risk_reward=data.risk_reward,
    )

    return result


# ==========================================
# Live Intelligent Decision API
# ==========================================


@router.get(
    "/intelligent/live/{symbol}",
    response_model=IntelligentDecisionResponse,
)
def analyze_live_intelligent_decision(
    symbol: str,
):
    """
    Generate a live intelligent trading decision.

    Uses real MetaTrader 5 market data and
    Aladdin's Decision Gate.

    This endpoint does NOT execute trades.
    It only provides decision support.
    """

    service = MarketIntelligenceService()

    try:

        # ==========================================
        # Generate Live Market Intelligence
        # ==========================================

        result = service.analyze(
            symbol=symbol,
        )

        intelligence = result["intelligence"]

        # ==========================================
        # Evaluate Decision Gate
        # ==========================================

        gate_result = (
            DecisionEngine.evaluate_gate(
                intelligence
            )
        )

        # ==========================================
        # Return Decision + Intelligence
        # ==========================================

        return {
            "symbol": symbol,

            "decision": {
                "action": (
                    gate_result.action
                ),

                "approved": (
                    gate_result.approved
                ),

                "market_confidence": (
                    gate_result.market_confidence
                ),

                "timeframe_confidence": (
                    gate_result.timeframe_confidence
                ),

                "decision_confidence": (
                    gate_result.decision_confidence
                ),

                "reason": (
                    gate_result.reason
                ),

                "gates_passed": (
                    gate_result.gates_passed
                ),

                "gates_failed": (
                    gate_result.gates_failed
                ),
            },

            "market_intelligence": {
                "market_bias": (
                    intelligence.market_bias
                ),

                "confidence": (
                    intelligence.confidence
                ),

                "risk_level": (
                    intelligence.risk_level
                ),

                "recommendation": (
                    intelligence.recommendation
                ),

                # ==================================
                # Market Structure
                # ==================================

                "structure_direction": (
                    intelligence.structure_direction
                ),

                "structure_confirmation": (
                    intelligence.structure_confirmation
                ),

                "structure_summary": (
                    intelligence.structure_summary
                ),

                # ==================================
                # Multi-Timeframe
                # ==================================

                "timeframe_alignment": (
                    intelligence.timeframe_alignment
                ),

                "timeframe_confidence": (
                    intelligence.timeframe_confidence
                ),

                "timeframe_summary": (
                    intelligence.timeframe_summary
                ),

                # ==================================
                # Market Session
                # ==================================

                "market_session": (
                    intelligence.market_session
                ),

                "session_activity": (
                    intelligence.session_activity
                ),

                "session_condition": (
                    intelligence.session_condition
                ),

                "session_summary": (
                    intelligence.session_summary
                ),

                # ==================================
                # Technical Analysis
                # ==================================

                "technical_summary": (
                    intelligence.technical_summary
                ),

                # ==================================
                # Economic News
                # ==================================

                "news_summary": (
                    intelligence.news_summary
                ),

                # ==================================
                # Agent Conflict
                # ==================================

                "conflict_detected": (
                    intelligence.conflict_detected
                ),

                "conflict_summary": (
                    intelligence.conflict_summary
                ),

                # ==================================
                # Confidence Explanation
                # ==================================

                "confidence_summary": (
                    intelligence.confidence_summary
                ),
            },
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except RuntimeError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Intelligent decision failed: "
                f"{error}"
            ),
        )

    finally:

        service.close()