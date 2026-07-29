"""
analytics_routes.py

Contains API endpoints related to trade analytics.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi import APIRouter, Depends

from app.dependencies.trade_dependencies import (
    get_trade_service,
)

from app.schemas import (
    TradeStatisticsSchema,
)

from app.services.trade_service import (
    TradeService,
)

from app.services.trade_analytics import (
    TradeAnalytics,
)


# Create analytics router
router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/",
    response_model=TradeStatisticsSchema,
)
def get_statistics(
    trade_service: TradeService = Depends(get_trade_service),
):
    """
    Return overall trading performance statistics.
    """

    # Load stored trades
    trades = trade_service.load_trades()

    # Create analytics object
    analytics = TradeAnalytics(
        trades
    )

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