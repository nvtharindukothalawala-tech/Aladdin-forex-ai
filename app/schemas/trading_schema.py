"""
trading_schema.py

Contains Pydantic schemas for
trading workflow API.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel, Field


class TradingRequest(BaseModel):
    """
    Input schema for complete trading workflow.
    """

    symbol: str = Field(
        ...,
        json_schema_extra={
            "example": "EUR/USD"
        },
    )

    trend: str = Field(
        ...,
        json_schema_extra={
            "example": "Bullish"
        },
    )

    momentum: str = Field(
        ...,
        json_schema_extra={
            "example": "Positive"
        },
    )

    risk_reward: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 3.0
        },
    )

    entry_price: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 1.1000
        },
    )

    stop_loss: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 1.0950
        },
    )

    take_profit: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 1.1100
        },
    )

    account_balance: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 10000
        },
    )

    risk_percent: float = Field(
        ...,
        gt=0,
        le=100,
        json_schema_extra={
            "example": 1
        },
    )

    trade_risk_amount: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 100
        },
    )

    lot_size: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 0.10
        },
    )