"""
performance_routes.py

Performance analytics API endpoints.

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


@router.get(
    "/performance",
    response_model=PerformanceResponse,
)
def get_performance(
    database: Session = Depends(get_database),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Return trading performance analytics
    for authenticated users.
    """

    repository = TradeRepository(database)

    service = PerformanceService(repository)

    return service.get_performance()
