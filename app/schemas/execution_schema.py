"""
execution_schema.py

API schemas for trade execution.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class ExecutionRequestSchema(BaseModel):
    """
    Input schema for execution request.
    """

    user_id: int

    symbol: str

    direction: str

    volume: float

    approved: bool


class ExecutionResponseSchema(BaseModel):
    """
    Response schema after execution.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    symbol: str

    direction: str

    volume: float

    status: str

    broker_order_id: str | None


class ExecutionHistoryResponseSchema(BaseModel):
    """
    Response schema for execution history.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    symbol: str

    direction: str

    volume: float

    status: str

    broker_order_id: str | None


class ExecutionStatisticsResponseSchema(BaseModel):
    """
    Response schema for execution statistics.
    """

    total_executions: int

    successful_executions: int

    failed_executions: int

    success_rate: float


class AIExecutionRequestSchema(BaseModel):
    """
    Input schema for complete AI-controlled
    trade analysis and execution workflow.

    Approval is not provided by the client.
    Aladdin determines approval internally.
    """

    user_id: int

    symbol: str = Field(
        ...,
        min_length=1,
    )

    ema_signal: str = Field(
        ...,
        pattern="^(BULLISH|BEARISH|NEUTRAL)$",
    )

    rsi_value: float

    adx_value: float

    volatility: str = Field(
        ...,
        pattern="^(NORMAL|HIGH)$",
    )

    currency: str

    event_type: str

    importance: str = Field(
        ...,
        pattern="^(HIGH|MEDIUM|LOW)$",
    )

    sentiment: str

    price_structure: str = "BOS_BULLISH"

    liquidity_sweep: bool = True

    order_block: str = "BULLISH"

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