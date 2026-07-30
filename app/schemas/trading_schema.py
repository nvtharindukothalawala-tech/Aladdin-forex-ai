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
        example="EUR/USD",
    )

    trend: str = Field(
        ...,
        example="Bullish",
    )

    momentum: str = Field(
        ...,
        example="Positive",
    )

    risk_reward: float = Field(
        ...,
        gt=0,
        example=3.0,
    )

    entry_price: float = Field(
        ...,
        gt=0,
        example=1.1000,
    )

    stop_loss: float = Field(
        ...,
        gt=0,
        example=1.0950,
    )

    take_profit: float = Field(
        ...,
        gt=0,
        example=1.1100,
    )

    account_balance: float = Field(
        ...,
        gt=0,
        example=10000,
    )


    risk_percent: float = Field(
        ...,
        gt=0,
        le=100,
        example=1,
    )


    trade_risk_amount: float = Field(
        ...,
        gt=0,
        example=100,
    )

    lot_size: float = Field(
        ...,
        gt=0,
        example=0.10,
    )
