"""
execution_routes.py

API endpoints for trade execution.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session


from app.database.connection import SessionLocal


from app.execution.execution_manager import (
    ExecutionManager,
)


from app.execution.repository import (
    ExecutionRepository,
)


from app.services.execution_service import (
    ExecutionService,
)


from app.schemas.execution_schema import (
    ExecutionRequestSchema,
    ExecutionResponseSchema,
    ExecutionHistoryResponseSchema,
)

router = APIRouter(
    prefix="/execution",
    tags=["Trade Execution"],
)


def get_database():

    session = SessionLocal()

    try:

        yield session

    finally:

        session.close()


@router.post(
    "/execute",
    response_model=ExecutionResponseSchema,
)
def execute_trade(
    request: ExecutionRequestSchema,
    database: Session = Depends(get_database),
):
    """
    Execute approved trade through MT5 layer.
    """

    repository = ExecutionRepository(database)

    service = ExecutionService(repository)

    execution_request = ExecutionManager.prepare_execution(
        symbol=request.symbol,
        direction=request.direction,
        lot_size=request.volume,
        approved=True,
    )

    result = service.execute_trade(
        user_id=request.user_id,
        execution_request=execution_request,
    )

    return result


@router.get(
    "/history/{user_id}",
    response_model=list[ExecutionHistoryResponseSchema],
)
def get_execution_history(
    user_id: int,
    database: Session = Depends(get_database),
):
    """
    Return execution history for a user.
    """

    repository = ExecutionRepository(database)

    executions = repository.get_user_executions(user_id)

    return executions
