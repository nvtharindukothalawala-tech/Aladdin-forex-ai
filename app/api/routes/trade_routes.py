"""
trade_routes.py

Contains API endpoints related to Forex trades.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.dependencies.trade_dependencies import (
    get_trade_service,
)

from app.auth.dependencies import (
    get_database,
    get_current_user,
)

from app.auth.models import UserModel

from app.database.notification_repository import (
    NotificationRepository,
)

from app.services.notification_service import (
    NotificationService,
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


# ==========================================
# Trade Router
# ==========================================

router = APIRouter(
    prefix="/trades",
    tags=["Trades"],
)


# ==========================================
# Get All Trades
# ==========================================

@router.get(
    "/",
    response_model=list[TradeResponseSchema],
)
def get_trades(
    trade_service: TradeService = Depends(
        get_trade_service
    ),
):
    """
    Get all trades.
    """

    return trade_service.load_trades()


# ==========================================
# Create Trade
# ==========================================

@router.post(
    "/",
    response_model=TradeResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_trade(
    trade_data: TradeCreateSchema,
    trade_service: TradeService = Depends(
        get_trade_service
    ),
    database: Session = Depends(get_database),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Create a new Forex trade and create
    a notification for the logged-in user.
    """

    # ------------------------------------------
    # Create Trade Object
    # ------------------------------------------

    trade = Trade(
        symbol=trade_data.symbol,
        direction=trade_data.direction,
        entry_price=trade_data.entry_price,
        lot_size=trade_data.lot_size,
        stop_loss=trade_data.stop_loss,
        take_profit=trade_data.take_profit,
    )

    # ------------------------------------------
    # Load Existing Trades
    # ------------------------------------------

    trade_service.load_trades()

    # ------------------------------------------
    # Add New Trade
    # ------------------------------------------

    trade_service.add_trade(trade)

    # ------------------------------------------
    # Create Notification
    # ------------------------------------------

    notification_repository = (
        NotificationRepository(database)
    )

    notification_service = NotificationService(
        notification_repository
    )

    notification_service.create_notification(
        user_id=current_user.id,
        notification_type="TRADE_CREATED",
        title="New Trade Created",
        message=(
            f"{trade.direction} trade created for "
            f"{trade.symbol}."
        ),
        trade_id=trade.trade_id,
        priority="INFO",
    )

    return trade


# ==========================================
# Close Trade
# ==========================================

@router.put(
    "/{trade_id}/close",
    response_model=TradeResponseSchema,
)
def close_trade(
    trade_id: str,
    close_data: TradeCloseSchema,
    trade_service: TradeService = Depends(
        get_trade_service
    ),
    database: Session = Depends(get_database),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Close an existing trade and create
    a notification for the logged-in user.
    """

    # ------------------------------------------
    # Load Trades
    # ------------------------------------------

    trade_service.load_trades()

    # ------------------------------------------
    # Find Trade
    # ------------------------------------------

    trade = trade_service.find_trade(
        trade_id
    )

    if trade is None:

        raise HTTPException(
            status_code=404,
            detail="Trade not found.",
        )

    # ------------------------------------------
    # Close Trade
    # ------------------------------------------

    trade.close_trade(
        close_data.exit_price
    )

    # ------------------------------------------
    # Save Trade
    # ------------------------------------------

    trade_service.save_trades()

    # ------------------------------------------
    # Calculate Profit / Loss
    # ------------------------------------------

    profit_loss = 0.0

    if (
        trade.exit_price is not None
        and trade.entry_price is not None
    ):

        price_difference = (
            trade.exit_price
            - trade.entry_price
        )

        if trade.direction.lower() == "sell":

            price_difference = (
                trade.entry_price
                - trade.exit_price
            )

        profit_loss = (
            price_difference
            * trade.lot_size
        )

    # ------------------------------------------
    # Determine Result
    # ------------------------------------------

    if profit_loss > 0:

        result = "Profit"
        priority = "SUCCESS"

    elif profit_loss < 0:

        result = "Loss"
        priority = "WARNING"

    else:

        result = "Break-even"
        priority = "INFO"

    # ------------------------------------------
    # Create Notification
    # ------------------------------------------

    notification_repository = (
        NotificationRepository(database)
    )

    notification_service = NotificationService(
        notification_repository
    )

    notification_service.create_notification(
        user_id=current_user.id,
        notification_type="TRADE_CLOSED",
        title="Trade Closed",
        message=(
            f"{trade.symbol} "
            f"{trade.direction} trade closed. "
            f"Result: {result}. "
            f"Profit/Loss: "
            f"{profit_loss:.4f}."
        ),
        trade_id=trade.trade_id,
        priority=priority,
    )

    return trade


# ==========================================
# Trade Statistics
# ==========================================

@router.get(
    "/statistics",
    response_model=TradeStatisticsSchema,
)
def get_trade_statistics(
    trade_service: TradeService = Depends(
        get_trade_service
    ),
):
    """
    Return trade performance statistics.
    """

    trades = trade_service.load_trades()

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