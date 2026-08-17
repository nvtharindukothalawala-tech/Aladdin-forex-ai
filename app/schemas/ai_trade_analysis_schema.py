"""
ai_trade_analysis_schema.py

Input schema for AI trade analysis.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel, Field


class AITradeAnalysisRequest(BaseModel):
    """
    Input schema for analysis-only AI trade setup.

    This endpoint analyzes the trade but does not execute it.
    """

    symbol: str = Field(
        ...,
        min_length=1,
        pattern=r".*\S.*",
        json_schema_extra={
            "example": "EUR/USD"
        },
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