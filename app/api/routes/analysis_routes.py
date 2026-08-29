"""
analysis_routes.py

Contains API endpoints for market analysis.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi import APIRouter, HTTPException

from app.analysis.market_analyzer import MarketAnalyzer
from app.schemas.analysis_schema import (
    MarketAnalysisRequest,
)
from app.services.market_analysis_service import (
    MarketAnalysisService,
)


router = APIRouter(
    prefix="/analysis",
    tags=["Market Analysis"],
)


@router.post("/market")
def analyze_market(
    data: MarketAnalysisRequest,
):
    """
    Analyze current market condition
    using supplied indicator values.
    """

    signal = MarketAnalyzer.analyze(
        symbol=data.symbol,
        current_price=data.current_price,
        ema=data.ema,
        sma=data.sma,
        rsi=data.rsi,
        atr=data.atr,
        adx=data.adx,
    )

    return signal


@router.get("/market/live/{symbol}")
def analyze_live_market(
    symbol: str,
):
    """
    Get real market data from MetaTrader 5
    and automatically perform technical analysis.
    """

    service = MarketAnalysisService()

    try:
        signal = service.analyze(
            symbol=symbol,
        )

        return signal

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
            detail=f"Market analysis failed: {error}",
        )

    finally:
        service.close()