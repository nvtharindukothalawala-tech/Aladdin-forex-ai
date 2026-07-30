"""
journal_routes.py

API endpoints for trade journal.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi import APIRouter


from app.database.connection import SessionLocal

from app.database.repository import TradeRepository

from app.services.journal_service import JournalService


from app.schemas.journal_schema import (
    JournalTradeResponse,
)

router = APIRouter(
    prefix="/journal",
    tags=["Trade Journal"],
)


def get_service():

    session = SessionLocal()

    repository = TradeRepository(session)

    return JournalService(repository)


@router.get(
    "/trades",
    response_model=list[JournalTradeResponse],
)
def get_trades():

    service = get_service()

    return service.get_trades()


@router.get("/count")
def get_trade_count():

    service = get_service()

    return {"total_trades": service.get_trade_count()}
