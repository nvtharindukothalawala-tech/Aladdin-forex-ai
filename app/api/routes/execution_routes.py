"""
execution_routes.py

API endpoints for trade execution.

Execution ownership is protected using the
authenticated JWT user.

Client-supplied user IDs are retained for API
compatibility, but they must match the authenticated
user before any user-owned execution data is accessed.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
)

from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_database,
    get_current_user,
)

from app.auth.models import UserModel

from app.database.notification_repository import (
    NotificationRepository,
)

from app.execution.execution_manager import (
    ExecutionManager,
)

from app.execution.repository import (
    ExecutionRepository,
)

from app.services.execution_service import (
    ExecutionIdempotencyConflictError,
    ExecutionService,
)

from app.services.execution_analytics_service import (
    ExecutionAnalyticsService,
)

from app.services.execution_reconciliation_service import (
    ExecutionReconciliationService,
)

from app.services.notification_service import (
    NotificationService,
)

from app.services.trading_service import (
    TradingService,
)

from app.schemas.execution_schema import (
    ExecutionRequestSchema,
    ExecutionResponseSchema,
    ExecutionHistoryResponseSchema,
    ExecutionStatisticsResponseSchema,
    ExecutionReconciliationResponseSchema,
    AIExecutionRequestSchema,
    AIExecutionResponseSchema,
)


# ==========================================
# Router
# ==========================================

router = APIRouter(
    prefix="/execution",
    tags=["Trade Execution"],
)


# ==========================================
# Ownership Validation
# ==========================================


def verify_execution_ownership(
    requested_user_id: int,
    current_user: UserModel,
) -> int:
    """
    Verify that a client-supplied user ID belongs
    to the currently authenticated user.

    The client user ID is kept only for backward
    API compatibility.

    The authenticated JWT user remains the
    authoritative identity.

    Args:
        requested_user_id:
            User ID supplied by the API request
            or URL path.

        current_user:
            User resolved from the authenticated
            JWT token.

    Returns:
        int:
            Authenticated user's database ID.

    Raises:
        HTTPException:
            403 when the requested user does not
            match the authenticated user.
    """

    authenticated_user_id = int(
        current_user.id
    )

    if (
        requested_user_id
        != authenticated_user_id
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "You are not authorized to access "
                "execution data for this user."
            ),
        )

    return authenticated_user_id


# ==========================================
# Direct Trade Execution
# ==========================================


@router.post(
    "/execute",
    response_model=ExecutionResponseSchema,
)
def execute_trade(
    request: ExecutionRequestSchema,
    database: Session = Depends(
        get_database
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Execute an approved trade through the MT5 layer.

    Execution ownership is derived from the
    authenticated JWT user.

    When an idempotency key is supplied, repeated
    requests for the same execution return the
    existing execution instead of contacting the
    broker again.
    """

    user_id = verify_execution_ownership(
        request.user_id,
        current_user,
    )

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
        ) from error

    try:

        result = service.execute_trade(
            user_id=user_id,
            execution_request=execution_request,
            idempotency_key=(
                request.idempotency_key
            ),
        )

    except ExecutionIdempotencyConflictError as error:

        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    return result


# ==========================================
# AI Trade Execution
# ==========================================


@router.post(
    "/ai-execute",
    response_model=AIExecutionResponseSchema,
    response_model_exclude_none=True,
)
def execute_ai_trade(
    request: AIExecutionRequestSchema,
    database: Session = Depends(
        get_database
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Run complete AI analysis,
    risk validation, approval,
    and execution workflow.

    The authenticated JWT user is the authoritative
    owner of the execution.

    The request user_id is retained for backward
    compatibility and must match the authenticated
    user.

    When the workflow reaches execution, the optional
    idempotency key is passed to the execution service
    to prevent accidental duplicate broker orders.
    """

    user_id = verify_execution_ownership(
        request.user_id,
        current_user,
    )

    # ==========================================
    # Execution Repository
    # ==========================================

    repository = ExecutionRepository(
        database
    )

    # ==========================================
    # Execution Service
    # ==========================================

    execution_service = ExecutionService(
        repository
    )

    # ==========================================
    # Notification Repository
    # ==========================================

    notification_repository = (
        NotificationRepository(
            database
        )
    )

    # ==========================================
    # Notification Service
    # ==========================================

    notification_service = (
        NotificationService(
            notification_repository
        )
    )

    # ==========================================
    # Complete AI Trading Workflow
    # ==========================================

    try:

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
                price_structure=(
                    request.price_structure
                ),
                liquidity_sweep=(
                    request.liquidity_sweep
                ),
                order_block=request.order_block,
                fair_value_gap=(
                    request.fair_value_gap
                ),
                entry_price=request.entry_price,
                stop_loss=request.stop_loss,
                take_profit=request.take_profit,
                account_balance=(
                    request.account_balance
                ),
                risk_percent=request.risk_percent,
                trade_risk_amount=(
                    request.trade_risk_amount
                ),
                lot_size=request.lot_size,
                execute=True,
                execution_service=(
                    execution_service
                ),
                notification_service=(
                    notification_service
                ),
                user_id=user_id,
                idempotency_key=(
                    request.idempotency_key
                ),
            )
        )

    except ExecutionIdempotencyConflictError as error:

        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    return result


# ==========================================
# Execution Reconciliation
# ==========================================


@router.post(
    "/reconcile-mt5/{user_id}",
    response_model=(
        ExecutionReconciliationResponseSchema
    ),
    response_model_exclude_none=True,
)
def reconcile_mt5_executions(
    user_id: int = Path(
        ...,
        gt=0,
    ),
    days: int = Query(
        default=30,
        ge=1,
        le=3650,
    ),
    database: Session = Depends(
        get_database
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Manually reconcile local PENDING execution
    records with read-only MT5 DEMO evidence.

    Security:
    - Authentication is required.
    - The requested user must match the
      authenticated JWT user.

    Reconciliation:
    - Requires DEMO execution mode.
    - Reads MT5 positions and trade history.
    - Uses ALADDIN E<execution_id> correlation.
    - Updates only confirmed local records.
    - Never opens, modifies, or closes broker trades.
    """

    authenticated_user_id = (
        verify_execution_ownership(
            user_id,
            current_user,
        )
    )

    repository = ExecutionRepository(
        database
    )

    service = (
        ExecutionReconciliationService(
            repository
        )
    )

    try:

        return (
            service
            .reconcile_pending_executions(
                user_id=(
                    authenticated_user_id
                ),
                days=days,
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except PermissionError as error:

        raise HTTPException(
            status_code=403,
            detail=str(error),
        ) from error

    except RuntimeError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error


# ==========================================
# Execution History
# ==========================================


@router.get(
    "/history/{user_id}",
    response_model=list[
        ExecutionHistoryResponseSchema
    ],
)
def get_execution_history(
    user_id: int = Path(
        ...,
        gt=0,
    ),
    database: Session = Depends(
        get_database
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Return execution history for the
    authenticated user.

    The requested user ID must match the
    authenticated JWT user.
    """

    authenticated_user_id = (
        verify_execution_ownership(
            user_id,
            current_user,
        )
    )

    repository = ExecutionRepository(
        database
    )

    executions = (
        repository.get_user_executions(
            authenticated_user_id
        )
    )

    return executions


# ==========================================
# Execution Statistics
# ==========================================


@router.get(
    "/statistics/{user_id}",
    response_model=(
        ExecutionStatisticsResponseSchema
    ),
)
def get_execution_statistics(
    user_id: int = Path(
        ...,
        gt=0,
    ),
    database: Session = Depends(
        get_database
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Return execution statistics for the
    authenticated user.

    The requested user ID must match the
    authenticated JWT user.
    """

    authenticated_user_id = (
        verify_execution_ownership(
            user_id,
            current_user,
        )
    )

    repository = ExecutionRepository(
        database
    )

    service = ExecutionAnalyticsService(
        repository
    )

    return service.get_statistics(
        authenticated_user_id
    )