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
    """

    user_id: int = Field(
        ...,
        gt=0,
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
# AI Execution Request
# ==========================================

class AIExecutionRequestSchema(BaseModel):
    """
    Input schema for complete AI-controlled
    trade analysis and execution workflow.

    Approval is not provided by the client.
    Aladdin determines approval internally.
    """

    user_id: int = Field(
        ...,
        gt=0,
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
        pattern="^(BOS_BULLISH|BOS_BEARISH|CHOCH|RANGE)$",
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
    # Legacy reasoning fields
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
    Response schema for the complete AI execution workflow.

    Optional workflow stages are omitted from the
    JSON response when they are not applicable.
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

    reasoning: AIReasoningResponseSchema | None = None

    execution: AIExecutionExecutionSchema | None = None

    execution_result: ExecutionResponseSchema | None = None