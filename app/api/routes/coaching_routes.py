"""
coaching_routes.py

AI coaching API endpoints.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi import APIRouter


from app.database.connection import SessionLocal

from app.database.repository import TradeRepository

from app.services.coaching_service import (
    CoachingService,
)


from app.schemas.coaching_schema import (
    CoachingResponse,
)

router = APIRouter(
    prefix="/coaching",
    tags=["AI Coaching"],
)


def get_service():

    session = SessionLocal()

    repository = TradeRepository(session)

    return CoachingService(repository)


@router.get(
    "/report",
    response_model=CoachingResponse,
)
def get_coaching_report():

    service = get_service()

    return service.generate_report()
