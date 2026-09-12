"""
journal_routes.py

API endpoints for trade journal.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.orm import Session


from app.auth.dependencies import (
    get_database,
    get_current_user,
)

from app.auth.models import UserModel


from app.database.repository import TradeRepository

from app.services.journal_service import JournalService


from app.schemas.journal_schema import JournalTradeResponse


router = APIRouter(
    prefix="/journal",
    tags=["Trade Journal"],
)


# ======================================================
# GET JOURNAL TRADES
# ======================================================

@router.get(
    "/trades",
    response_model=list[JournalTradeResponse],
)
def get_trades(
    database: Session = Depends(
        get_database
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Return journal trades
    for the authenticated user.
    """

    repository = TradeRepository(
        database
    )

    service = JournalService(
        repository
    )

    return service.get_trades(
        current_user.id
    )


# ======================================================
# GET JOURNAL TRADE COUNT
# ======================================================

@router.get(
    "/count"
)
def get_trade_count(
    database: Session = Depends(
        get_database
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Return total journal trades
    for the authenticated user.
    """

    repository = TradeRepository(
        database
    )

    service = JournalService(
        repository
    )

    return {
        "total_trades": (
            service.get_trade_count(
                current_user.id
            )
        )
    }


# ======================================================
# SYNC MT5 COMPLETED POSITIONS
# ======================================================

@router.post(
    "/sync-mt5"
)
def sync_mt5_history(
    days: int = Query(
        default=30,
        ge=1,
        le=3650,
        description=(
            "Number of MT5 history days "
            "to check."
        ),
    ),
    include_other_trades: bool = Query(
        default=False,
        description=(
            "When false, only completed "
            "Aladdin MT5 trades are imported."
        ),
    ),
    database: Session = Depends(
        get_database
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Synchronize completed MT5 positions
    into the authenticated user's journal.

    Default behavior:
        Only trades identified as Aladdin
        trades are imported.

    Duplicate trades:
        Existing MT5 deal tickets are
        ignored safely.

    Safety:
        This endpoint only reads MT5
        history and writes journal records.

        It does NOT open, modify,
        or close MT5 positions.
    """

    repository = TradeRepository(
        database
    )

    service = JournalService(
        repository
    )

    return service.sync_mt5_closed_trades(
        user_id=current_user.id,
        days=days,
        include_other_trades=(
            include_other_trades
        ),
    )