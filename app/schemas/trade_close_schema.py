"""
trade_close_schema.py

Contains Pydantic schema for closing trades.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel, Field


class TradeCloseSchema(BaseModel):
    """
    Schema used when closing an existing trade.

    Validates the exit price received from API.
    """

    exit_price: float = Field(
        ...,
        gt=0,
        example=1.0850,
    )