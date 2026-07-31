"""
coaching_routes.py

AI coaching API endpoints.

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


@router.get(
    "/report",
    response_model=CoachingResponse,
)
def get_coaching_report(
    database: Session = Depends(get_database),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Return AI coaching report
    for authenticated users.
    """

    repository = TradeRepository(database)

    service = CoachingService(repository)

    return service.generate_report()
