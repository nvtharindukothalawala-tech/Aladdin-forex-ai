"""
execution_schema.py

API schemas for trade execution.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# ==========================================
# Direct Execution Request
# ==========================================

class ExecutionRequestSchema(BaseModel):
    """
    Input schema for direct execution request.

    idempotency_key is optional for backward
    compatibility. Clients that provide it receive
    duplicate-execution protection.
    """

    user_id: int = Field(
        ...,
        gt=0,
    )

    idempotency_key: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
        pattern=r".*\S.*",
    )

    symbol: str = Field(
        ...,
        min_length=1,
        pattern=r".*\S.*",
    )

    direction: str = Field(
        ...,
        pattern="^(BUY|SELL)$",
    )

    volume: float = Field(
        ...,
        gt=0,
    )

    approved: bool

    entry_price: float | None = Field(
        default=None,
        gt=0,
    )

    stop_loss: float | None = Field(
        default=None,
        gt=0,
    )

    take_profit: float | None = Field(
        default=None,
        gt=0,
    )


# ==========================================
# Execution Response
# ==========================================

class ExecutionResponseSchema(BaseModel):
    """
    Response schema after execution.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    symbol: str

    direction: str

    volume: float

    status: str

    broker_order_id: str | None = None

    execution_message: str | None = None

    execution_mode: str | None = None

    demo_execution_enabled: bool | None = None


# ==========================================
# Execution History Response
# ==========================================

class ExecutionHistoryResponseSchema(BaseModel):
    """
    Response schema for execution history.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    symbol: str

    direction: str

    volume: float

    status: str

    broker_order_id: str | None = None

    execution_message: str | None = None


# ==========================================
# Execution Statistics Response
# ==========================================

class ExecutionStatisticsResponseSchema(BaseModel):
    """
    Response schema for execution statistics.
    """

    total_executions: int

    successful_executions: int

    failed_executions: int

    success_rate: float


# ==========================================
# Execution Reconciliation Item
# ==========================================

class ExecutionReconciledItemSchema(BaseModel):
    """
    One successfully reconciled execution.
    """

    execution_id: int

    symbol: str

    direction: str

    volume: float

    broker_order_id: str

    evidence_source: str


# ==========================================
# Execution Reconciliation Unmatched Item
# ==========================================

class ExecutionUnmatchedItemSchema(BaseModel):
    """
    One PENDING execution with no exact
    broker correlation.
    """

    execution_id: int

    symbol: str

    direction: str

    volume: float

    reason: str


# ==========================================
# Execution Reconciliation Conflict Item
# ==========================================

class ExecutionConflictItemSchema(BaseModel):
    """
    One reconciliation conflict.

    A conflict may occur because:
    - Multiple broker records use the same
      execution correlation ID.
    - Broker symbol/direction/volume does not
      match the local execution.
    - A broker identifier is unavailable.
    """

    execution_id: int

    symbol: str

    direction: str

    volume: float

    reason: str

    evidence_source: str | None = None

    evidence_count: int | None = None

    errors: list[str] | None = None


# ==========================================
# Execution Reconciliation Response
# ==========================================

class ExecutionReconciliationResponseSchema(
    BaseModel
):
    """
    Response from manual MT5 execution
    reconciliation.

    Reconciliation is read-only on the broker
    side. Only confirmed local PENDING records
    are changed to EXECUTED.
    """

    execution_mode: str

    history_days: int

    scanned_pending: int

    reconciled_count: int

    unmatched_count: int

    conflict_count: int

    reconciled: list[
        ExecutionReconciledItemSchema
    ]

    unmatched: list[
        ExecutionUnmatchedItemSchema
    ]

    conflicts: list[
        ExecutionConflictItemSchema
    ]

    message: str


# ==========================================
# AI Execution Request
# ==========================================

class AIExecutionRequestSchema(BaseModel):
    """
    Input schema for complete AI-controlled
    trade analysis and execution workflow.

    Approval is not provided by the client.
    Aladdin determines approval internally.

    idempotency_key is optional for backward
    compatibility. Clients that provide it receive
    duplicate-execution protection if the workflow
    reaches the execution stage.
    """

    user_id: int = Field(
        ...,
        gt=0,
    )

    idempotency_key: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
        pattern=r".*\S.*",
    )

    symbol: str = Field(
        ...,
        min_length=1,
        pattern=r".*\S.*",
    )

    ema_signal: str = Field(
        ...,
        pattern="^(BULLISH|BEARISH|NEUTRAL)$",
    )

    rsi_value: float = Field(
        ...,
        ge=0,
        le=100,
    )

    adx_value: float = Field(
        ...,
        ge=0,
        le=100,
    )

    volatility: str = Field(
        ...,
        pattern="^(NORMAL|HIGH)$",
    )

    currency: str = Field(
        ...,
        min_length=1,
        pattern=r".*\S.*",
    )

    event_type: str = Field(
        ...,
        min_length=1,
        pattern=r".*\S.*",
    )

    importance: str = Field(
        ...,
        pattern="^(HIGH|MEDIUM|LOW)$",
    )

    sentiment: str = Field(
        ...,
        pattern="^(BULLISH|BEARISH|NEUTRAL)$",
    )

    price_structure: str = Field(
        default="BOS_BULLISH",
        pattern=(
            "^(BOS_BULLISH|BOS_BEARISH|"
            "CHOCH|RANGE)$"
        ),
    )

    liquidity_sweep: bool = True

    order_block: str = Field(
        default="BULLISH",
        pattern="^(BULLISH|BEARISH)$",
    )

    fair_value_gap: bool = True

    entry_price: float = Field(
        ...,
        gt=0,
    )

    stop_loss: float = Field(
        ...,
        gt=0,
    )

    take_profit: float = Field(
        ...,
        gt=0,
    )

    account_balance: float = Field(
        ...,
        gt=0,
    )

    risk_percent: float = Field(
        ...,
        gt=0,
        le=100,
    )

    trade_risk_amount: float = Field(
        ...,
        gt=0,
    )

    lot_size: float = Field(
        ...,
        gt=0,
    )


# ==========================================
# AI Execution Information
# ==========================================

class AIExecutionExecutionSchema(BaseModel):
    """
    Prepared execution information returned
    by the AI execution workflow.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    symbol: str

    order_type: str

    volume: float

    status: str

    entry_price: float | None = None

    stop_loss: float | None = None

    take_profit: float | None = None


# ==========================================
# AI Reasoning Response
# ==========================================

class AIReasoningResponseSchema(BaseModel):
    """
    Explainable AI reasoning returned by the
    AI trade execution workflow.

    The legacy reasoning fields are kept for
    backward compatibility with the existing
    ReasoningEngine contract.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
    )

    decision: str | None = None

    confidence: float | None = None

    technical_reason: str | None = None

    news_reason: str | None = None

    structure_reason: str | None = None

    risk_reason: str | None = None

    timeframe_reason: str | None = None

    session_reason: str | None = None

    final_reason: str | None = None

    # ==========================================
    # Decision Gate Reasoning
    # ==========================================

    gate_reason: str | None = None

    gates_passed: list[str] | None = None

    gates_failed: list[str] | None = None

    # ==========================================
    # Legacy Reasoning Fields
    # ==========================================

    technical_reasons: list[str] | None = None

    structure_reasons: list[str] | None = None

    risk_reasons: list[str] | None = None

    final_message: str | None = None


# ==========================================
# AI Execution Response
# ==========================================

class AIExecutionResponseSchema(BaseModel):
    """
    Response schema for the complete
    AI execution workflow.

    Optional workflow stages are omitted
    when they are not applicable.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
    )

    decision: Any | None = None

    market_intelligence: Any | None = None

    trade_plan: Any | None = None

    risk_validation: Any | None = None

    approval: Any | None = None

    reasoning: (
        AIReasoningResponseSchema
        | None
    ) = None

    execution: (
        AIExecutionExecutionSchema
        | None
    ) = None

    execution_result: (
        ExecutionResponseSchema
        | None
    ) = None