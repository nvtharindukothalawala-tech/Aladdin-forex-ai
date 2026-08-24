"""
intelligence_routes.py

API endpoints for Aladdin market intelligence.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi import APIRouter, HTTPException

from app.services.market_intelligence_service import (
    MarketIntelligenceService,
)


router = APIRouter(
    prefix="/intelligence",
    tags=["Market Intelligence"],
)


@router.get("/market/live/{symbol}")
def analyze_live_intelligence(
    symbol: str,
):
    """
    Analyze live market intelligence using
    real MetaTrader 5 market data.
    """

    service = MarketIntelligenceService()

    try:

        result = service.analyze(
            symbol=symbol,
        )

        return result

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
            detail=f"Market intelligence failed: {error}",
        )

    finally:

        service.close()