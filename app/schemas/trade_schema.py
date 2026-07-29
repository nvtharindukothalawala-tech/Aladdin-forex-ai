"""
trade_schema.py

Contains Pydantic schemas for trade data validation.

These schemas prepare the Aladdin Forex Trading Assistant
for future API integration.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel, Field


class TradeCreateSchema(BaseModel):
    """
    Schema used when creating a new trade.

    This validates incoming trade information
    before creating a Trade object.
    """

    # Forex pair name
    symbol: str = Field(
        ...,
        example="EUR/USD",
    )

    # Trade direction
    direction: str = Field(
        ...,
        example="Buy",
    )

    # Entry price of the trade
    entry_price: float = Field(
        ...,
        gt=0,
        example=1.0800,
    )

    # Trading volume
    lot_size: float = Field(
        ...,
        gt=0,
        example=0.10,
    )

    # Stop loss price
    stop_loss: float = Field(
        ...,
        gt=0,
        example=1.0750,
    )

    # Take profit price
    take_profit: float = Field(
        ...,
        gt=0,
        example=1.0900,
    )