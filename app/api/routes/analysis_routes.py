"""
analysis_routes.py

Contains API endpoints for market analysis.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi import APIRouter

from app.analysis.market_analyzer import MarketAnalyzer
from app.schemas.analysis_schema import (
    MarketAnalysisRequest,
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
    Analyze current market condition.
    """

    signal = MarketAnalyzer.analyze(
        symbol=data.symbol,
        current_price=data.current_price,
        sma=data.sma,
        rsi=data.rsi,
        atr=data.atr,
    )

    return signal
