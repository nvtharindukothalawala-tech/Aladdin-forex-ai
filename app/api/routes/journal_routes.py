"""
journal_routes.py

API endpoints for trade journal.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi import APIRouter, Depends
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


@router.get(
    "/trades",
    response_model=list[JournalTradeResponse],
)
def get_trades(
    database: Session = Depends(get_database),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Return all journal trades for authenticated users.
    """

    repository = TradeRepository(database)

    service = JournalService(repository)

    return service.get_trades()


@router.get("/count")
def get_trade_count(
    database: Session = Depends(get_database),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Return total number of journal trades.
    """

    repository = TradeRepository(database)

    service = JournalService(repository)

    return {"total_trades": service.get_trade_count()}
