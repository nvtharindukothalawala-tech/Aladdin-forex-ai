"""
trade_routes.py

Contains API endpoints related to Forex trades.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.dependencies.trade_dependencies import (
    get_trade_service,
)

from app.models.trade import Trade

from app.schemas import (
    TradeCreateSchema,
    TradeResponseSchema,
    TradeCloseSchema,
    TradeStatisticsSchema,
)

from app.services.trade_service import TradeService
from app.services.trade_analytics import TradeAnalytics


# Create trade router
router = APIRouter(
    prefix="/trades",
    tags=["Trades"],
)


@router.get(
    "/",
    response_model=list[TradeResponseSchema],
)
def get_trades(
    trade_service: TradeService = Depends(get_trade_service),
):
    """
    Get all trades.
    """

    return trade_service.load_trades()



@router.post(
    "/",
    response_model=TradeResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_trade(
    trade_data: TradeCreateSchema,
    trade_service: TradeService = Depends(get_trade_service),
):
    """
    Create a new Forex trade.
    """

    trade = Trade(
        symbol=trade_data.symbol,
        direction=trade_data.direction,
        entry_price=trade_data.entry_price,
        lot_size=trade_data.lot_size,
        stop_loss=trade_data.stop_loss,
        take_profit=trade_data.take_profit,
    )

    trade_service.load_trades()

    trade_service.add_trade(trade)

    return trade



@router.put(
    "/{trade_id}/close",
    response_model=TradeResponseSchema,
)
def close_trade(
    trade_id: str,
    close_data: TradeCloseSchema,
    trade_service: TradeService = Depends(get_trade_service),
):
    """
    Close an existing trade.
    """

    trade_service.load_trades()

    trade = trade_service.find_trade(trade_id)

    if trade is None:
        raise HTTPException(
            status_code=404,
            detail="Trade not found.",
        )

    trade.close_trade(
        close_data.exit_price
    )

    trade_service.save_trades()

    return trade



@router.get(
    "/statistics",
    response_model=TradeStatisticsSchema,
)
def get_trade_statistics(
    trade_service: TradeService = Depends(get_trade_service),
):
    """
    Return trade performance statistics.
    """

    trades = trade_service.load_trades()

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