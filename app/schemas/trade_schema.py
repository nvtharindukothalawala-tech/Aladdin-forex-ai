"""
trade_schema.py

Contains Pydantic schemas for trade data validation.

These schemas prepare the Aladdin Forex Trading Assistant
for future API integration.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from datetime import datetime

from pydantic import BaseModel, Field


class TradeCreateSchema(BaseModel):
    """
    Schema used when creating a new trade.

    This validates incoming trade information
    before creating a Trade object.
    """

    symbol: str = Field(
        ...,
        json_schema_extra={
            "example": "EUR/USD"
        },
    )

    direction: str = Field(
        ...,
        json_schema_extra={
            "example": "Buy"
        },
    )

    entry_price: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 1.0800
        },
    )

    lot_size: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 0.10
        },
    )

    stop_loss: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 1.0750
        },
    )

    take_profit: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 1.0900
        },
    )


class TradeResponseSchema(BaseModel):
    """
    Schema used when returning trade information
    through the API.

    This controls what data is visible to clients.
    """

    trade_id: str

    symbol: str

    direction: str

    entry_price: float

    exit_price: float | None

    lot_size: float

    stop_loss: float

    take_profit: float

    status: str

    open_time: datetime

    close_time: datetime | None

    strategy: str

    reason: str

    emotion: str

    lesson_learned: str