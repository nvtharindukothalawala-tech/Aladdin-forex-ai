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
    database: Session = Depends(
        get_database
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Create a new Forex trade.

    After successfully creating the trade,
    a notification is created for the
    authenticated user.
    """

    # --------------------------------------
    # Create Trade Object
    # --------------------------------------

    trade = Trade(
        symbol=trade_data.symbol,
        direction=trade_data.direction,
        entry_price=trade_data.entry_price,
        lot_size=trade_data.lot_size,
        stop_loss=trade_data.stop_loss,
        take_profit=trade_data.take_profit,
    )

    # --------------------------------------
    # Load Existing Trades
    # --------------------------------------

    trade_service.load_trades()

    # --------------------------------------
    # Add New Trade
    # --------------------------------------

    try:

        trade_service.add_trade(trade)

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    # --------------------------------------
    # Create Notification
    # --------------------------------------

    try:

        notification_repository = (
            NotificationRepository(database)
        )

        notification_service = (
            NotificationService(
                notification_repository
            )
        )

        notification_service.create_notification(
            user_id=current_user.id,
            notification_type="TRADE_CREATED",
            title="New Trade Created",
            message=(
                f"{trade.direction} trade created "
                f"for {trade.symbol}."
            ),
            trade_id=trade.trade_id,
            priority="INFO",
        )

    except Exception as error:

        # The trade has already been saved.
        # Notification failure should not
        # delete or break the trade.

        print(
            "Notification creation failed:",
            error,
        )

    # --------------------------------------
    # Return Created Trade
    # --------------------------------------

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
    database: Session = Depends(
        get_database
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Close an existing trade.

    After successfully closing the trade,
    a notification is created for the
    authenticated user.
    """

    # --------------------------------------
    # Load Trades
    # --------------------------------------

    trade_service.load_trades()

    # --------------------------------------
    # Find Trade
    # --------------------------------------

    trade = trade_service.find_trade(
        trade_id
    )

    if trade is None:

        raise HTTPException(
            status_code=404,
            detail="Trade not found.",
        )

    # --------------------------------------
    # Close Trade
    # --------------------------------------

    trade.close_trade(
        close_data.exit_price
    )

    # --------------------------------------
    # Save Trade
    # --------------------------------------

    trade_service.save_trades()

    # --------------------------------------
    # Create Notification
    # --------------------------------------

    try:

        notification_repository = (
            NotificationRepository(database)
        )

        notification_service = (
            NotificationService(
                notification_repository
            )
        )

        notification_service.create_notification(
            user_id=current_user.id,
            notification_type="TRADE_CLOSED",
            title="Trade Closed",
            message=(
                f"{trade.symbol} trade has been "
                f"closed."
            ),
            trade_id=trade.trade_id,
            priority="INFO",
        )

    except Exception as error:

        # The trade has already been saved.
        # Notification failure should not
        # break the close operation.

        print(
            "Notification creation failed:",
            error,
        )

    # --------------------------------------
    # Return Closed Trade
    # --------------------------------------

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

    analytics = TradeAnalytics(
        trades
    )

    return {
        "total_trades": (
            analytics.total_trades()
        ),
        "open_trades": (
            analytics.open_trades()
        ),
        "winning_trades": (
            analytics.winning_trades()
        ),
        "losing_trades": (
            analytics.losing_trades()
        ),
        "win_rate": (
            analytics.win_rate()
        ),
        "total_profit": (
            analytics.total_profit()
        ),
        "average_profit": (
            analytics.average_profit()
        ),
        "profit_factor": (
            analytics.profit_factor()
        ),
    }