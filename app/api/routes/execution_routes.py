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



from app.execution.execution_safety_context import (

    ExecutionSafetyContext,

)



from app.market.mt5_provider import (

    MT5DataProvider,

)



from app.execution.repository import (

    ExecutionRepository,

)



from app.services.execution_service import (

    ExecutionIdempotencyConflictError,

    ExecutionSafetyRejectedError,

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

    ExecutionReconciliationAuditSchema,

    AIExecutionRequestSchema,

    AIExecutionResponseSchema,

    ApprovedAIExecutionRequestSchema,

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



    Optional Entry, Stop Loss and Take Profit

    values are forwarded to ExecutionManager

    when supplied.



    When an idempotency key is supplied,

    repeated requests for the same execution

    return the existing execution instead of

    contacting the broker again.

    """



    # ==========================================

    # Authenticated User Ownership

    # ==========================================



    user_id = verify_execution_ownership(

        request.user_id,

        current_user,

    )



    # ==========================================

    # Repository / Service

    # ==========================================



    repository = ExecutionRepository(

        database

    )



    service = ExecutionService(

        repository

    )



    # ==========================================

    # Prepare Execution

    # ==========================================



    try:



        execution_request = (

            ExecutionManager.prepare_execution(

                symbol=request.symbol,

                direction=request.direction,

                lot_size=request.volume,

                approved=request.approved,

                entry_price=request.entry_price,

                stop_loss=request.stop_loss,

                take_profit=request.take_profit,

            )

        )



    except ValueError as error:



        raise HTTPException(

            status_code=403,

            detail=str(error),

        ) from error



    # ==========================================

    # Execute Trade

    # ==========================================



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
# Approved Deterministic AI Trade Execution
# ==========================================

@router.post(
    "/approved-ai-execute",
    response_model=ExecutionResponseSchema,
)
def execute_approved_ai_trade(
    request: ApprovedAIExecutionRequestSchema,
    database: Session = Depends(get_database),
    current_user: UserModel = Depends(get_current_user),
):
    """Execute an already-approved deterministic trade setup."""
    user_id = verify_execution_ownership(request.user_id, current_user)

    if not request.setup_approved:
        raise HTTPException(status_code=403, detail="Trade setup is not approved for execution.")
    if not request.risk_approved:
        raise HTTPException(status_code=403, detail="Pre-trade risk analysis is not approved.")
    if request.setup_engine != "DETERMINISTIC":
        raise HTTPException(status_code=403, detail="Unsupported trade setup engine.")
    if request.risk_engine != "DETERMINISTIC":
        raise HTTPException(status_code=403, detail="Unsupported risk engine.")

    direction = request.direction.strip().upper()
    if direction == "BUY":
        if not (request.stop_loss < request.entry_price < request.take_profit):
            raise HTTPException(
                status_code=422,
                detail="Invalid BUY price structure. Required: stop_loss < entry_price < take_profit.",
            )
    elif direction == "SELL":
        if not (request.take_profit < request.entry_price < request.stop_loss):
            raise HTTPException(
                status_code=422,
                detail="Invalid SELL price structure. Required: take_profit < entry_price < stop_loss.",
            )
    else:
        raise HTTPException(status_code=422, detail="Trade direction must be BUY or SELL.")

    tolerance = max(1e-9, request.risk_amount * 1e-9)
    if request.estimated_loss > request.risk_amount + tolerance:
        raise HTTPException(
            status_code=403,
            detail="Estimated trade loss exceeds the approved risk amount.",
        )

    repository = ExecutionRepository(database)
    execution_service = ExecutionService(repository)

    try:
        execution_request = ExecutionManager.prepare_execution(
            symbol=request.symbol,
            direction=direction,
            lot_size=request.volume,
            approved=True,
            entry_price=request.entry_price,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    mt5_provider = MT5DataProvider()
    try:
        quote = mt5_provider.get_quote(request.symbol)
        symbol_info = mt5_provider.get_symbol_risk_info(request.symbol)
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to load fresh MT5 execution safety data: {error}",
        ) from error
    finally:
        try:
            mt5_provider.disconnect()
        except Exception:
            pass

    if not isinstance(quote, dict):
        raise HTTPException(status_code=503, detail="MT5 quote information is unavailable.")
    if not isinstance(symbol_info, dict):
        raise HTTPException(status_code=503, detail="MT5 symbol information is unavailable.")

    safety_trade_setup = {
        "status": "TRADE",
        "symbol": request.symbol,
        "timeframe": request.timeframe,
        "direction": direction,
        "entry": {"preferred": request.entry_price},
        "stop_loss": request.stop_loss,
        "take_profit": request.take_profit,
        "targets": [{"name": "TP1", "price": request.take_profit}],
        "engine": request.setup_engine,
    }

    safety_risk = {
        "status": "APPROVED",
        "approved": True,
        "symbol": request.symbol,
        "timeframe": request.timeframe,
        "direction": direction,
        "risk_percent": request.risk_percent,
        "risk_amount": request.risk_amount,
        "estimated_loss": request.estimated_loss,
        "entry_price": request.entry_price,
        "stop_loss": request.stop_loss,
        "volume": request.volume,
        "engine": request.risk_engine,
    }

    safety_context = ExecutionSafetyContext(
        trade_setup=safety_trade_setup,
        risk=safety_risk,
        quote=quote,
        symbol_info=symbol_info,
    )

    try:
        return execution_service.execute_trade(
            user_id=user_id,
            execution_request=execution_request,
            idempotency_key=request.idempotency_key,
            safety_context=safety_context,
        )
    except ExecutionIdempotencyConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except ExecutionSafetyRejectedError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error


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

# Reconciliation Audit History

# ==========================================





@router.get(

    "/reconciliation-audits/{user_id}",

    response_model=list[

        ExecutionReconciliationAuditSchema

    ],

)

def get_reconciliation_audits(

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

    Return persisted reconciliation audit records

    for the authenticated user.



    This endpoint is read-only.



    It does not:

    - contact MT5,

    - perform reconciliation,

    - modify execution records.

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



    return (

        repository

        .get_user_reconciliation_audits(

            authenticated_user_id

        )

    )





# ==========================================

# Execution Reconciliation Audit History

# ==========================================





@router.get(

    "/reconciliation-audits/{user_id}/{execution_id}",

    response_model=list[

        ExecutionReconciliationAuditSchema

    ],

)

def get_execution_reconciliation_audits(

    user_id: int = Path(

        ...,

        gt=0,

    ),

    execution_id: int = Path(

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

    Return reconciliation audit records for one

    execution belonging to the authenticated user.



    This endpoint is read-only and does not contact

    the broker.

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



    return (

        repository

        .get_execution_reconciliation_audits(

            execution_id=execution_id,

            user_id=authenticated_user_id,

        )

    )



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