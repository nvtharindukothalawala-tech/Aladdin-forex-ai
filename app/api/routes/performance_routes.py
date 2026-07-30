"""
performance_routes.py

Performance analytics API endpoints.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi import APIRouter


from app.database.connection import SessionLocal

from app.database.repository import TradeRepository

from app.services.performance_service import (
    PerformanceService,
)


from app.schemas.performance_response_schema import (
    PerformanceResponse,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Performance Analytics"],
)


def get_service():

    session = SessionLocal()

    repository = TradeRepository(session)

    return PerformanceService(repository)


@router.get(
    "/performance",
    response_model=PerformanceResponse,
)
def get_performance():

    service = get_service()

    return service.get_performance()
