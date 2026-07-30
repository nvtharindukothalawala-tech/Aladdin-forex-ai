"""
analytics_routes.py

Contains API endpoints related to trade analytics.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi import APIRouter, Depends

from app.dependencies.trade_dependencies import get_trade_service
from app.schemas import (
    PerformanceSchema,
    TradeStatisticsSchema,
)
from app.services.trade_analytics import TradeAnalytics
from app.services.trade_service import TradeService

# Create analytics router
router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# ==========================================
# General Statistics Endpoint
# ==========================================


@router.get(
    "/",
    response_model=TradeStatisticsSchema,
)
def get_statistics(
    trade_service: TradeService = Depends(get_trade_service),
):
    """
    Return general trading statistics.

    Args:
        trade_service: Trade service provided by FastAPI
        dependency injection.

    Returns:
        TradeStatisticsSchema: General trade statistics.
    """

    # Load all trades from storage.
    trades = trade_service.load_trades()

    # Create the analytics service using the loaded trades.
    analytics = TradeAnalytics(trades)

    return {
        "total_trades": analytics.total_trades(),
        "open_trades": analytics.open_trades(),
        "winning_trades": analytics.winning_trades(),
        "losing_trades": analytics.losing_trades(),
        "win_rate": analytics.win_rate(),
        "total_profit": analytics.total_profit(),
        "average_profit": analytics.average_profit(),
        "profit_factor": analytics.profit_factor(),
    }


# ==========================================
# Performance Endpoint
# ==========================================


@router.get(
    "/performance",
    response_model=PerformanceSchema,
)
def get_performance(
    trade_service: TradeService = Depends(get_trade_service),
):
    """
    Return detailed trade performance information.

    Args:
        trade_service: Trade service provided by FastAPI
        dependency injection.

    Returns:
        PerformanceSchema: Trading performance summary.
    """

    # Load all trades from storage.
    trades = trade_service.load_trades()

    # Create the analytics service.
    analytics = TradeAnalytics(trades)

    # Find the best and worst closed trades.
    best_trade = analytics.best_trade()
    worst_trade = analytics.worst_trade()

    return {
        "total_trades": analytics.total_trades(),
        "winning_trades": analytics.winning_trades(),
        "losing_trades": analytics.losing_trades(),
        "win_rate": analytics.win_rate(),
        "total_profit": analytics.total_profit(),
        "average_profit": analytics.average_profit(),
        "best_trade": (best_trade.trade_id if best_trade is not None else None),
        "worst_trade": (worst_trade.trade_id if worst_trade is not None else None),
    }
