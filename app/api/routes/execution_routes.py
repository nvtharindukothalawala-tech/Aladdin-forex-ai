"""
execution_routes.py

API endpoints for trade execution.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

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

from app.services.execution_analytics_service import (
    ExecutionAnalyticsService,
)

from app.services.trading_service import (
    TradingService,
)

from app.schemas.execution_schema import (
    ExecutionRequestSchema,
    ExecutionResponseSchema,
    ExecutionHistoryResponseSchema,
    ExecutionStatisticsResponseSchema,
    AIExecutionRequestSchema,
)


router = APIRouter(
    prefix="/execution",
    tags=["Trade Execution"],
)


def get_database():
    """
    Provide database session.
    """

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

    repository = ExecutionRepository(
        database
    )

    service = ExecutionService(
        repository
    )

    try:
        execution_request = (
            ExecutionManager.prepare_execution(
                symbol=request.symbol,
                direction=request.direction,
                lot_size=request.volume,
                approved=request.approved,
            )
        )

    except ValueError as error:
        raise HTTPException(
            status_code=403,
            detail=str(error),
        )

    result = service.execute_trade(
        user_id=request.user_id,
        execution_request=execution_request,
    )

    return result


@router.post("/ai-execute")
def execute_ai_trade(
    request: AIExecutionRequestSchema,
    database: Session = Depends(get_database),
):
    """
    Run complete AI analysis,
    risk validation, approval,
    and execution workflow.
    """

    repository = ExecutionRepository(
        database
    )

    execution_service = ExecutionService(
        repository
    )

    result = (
        TradingService.generate_ai_execution_workflow(
            symbol=request.symbol,
            ema_signal=request.ema_signal,
            rsi_value=request.rsi_value,
            adx_value=request.adx_value,
            volatility=request.volatility,
            currency=request.currency,
            event_type=request.event_type,
            importance=request.importance,
            sentiment=request.sentiment,
            price_structure=request.price_structure,
            liquidity_sweep=request.liquidity_sweep,
            order_block=request.order_block,
            fair_value_gap=request.fair_value_gap,
            entry_price=request.entry_price,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
            account_balance=request.account_balance,
            risk_percent=request.risk_percent,
            trade_risk_amount=(
                request.trade_risk_amount
            ),
            lot_size=request.lot_size,
            execute=True,
            execution_service=execution_service,
            user_id=request.user_id,
        )
    )

    return result


@router.get(
    "/history/{user_id}",
    response_model=list[
        ExecutionHistoryResponseSchema
    ],
)
def get_execution_history(
    user_id: int,
    database: Session = Depends(get_database),
):
    """
    Return execution history for a user.
    """

    repository = ExecutionRepository(
        database
    )

    executions = repository.get_user_executions(
        user_id
    )

    return executions


@router.get(
    "/statistics/{user_id}",
    response_model=ExecutionStatisticsResponseSchema,
)
def get_execution_statistics(
    user_id: int,
    database: Session = Depends(get_database),
):
    """
    Return execution statistics for a user.
    """

    repository = ExecutionRepository(
        database
    )

    service = ExecutionAnalyticsService(
        repository
    )

    return service.get_statistics(
        user_id
    )