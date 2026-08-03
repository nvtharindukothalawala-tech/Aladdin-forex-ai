"""
risk_schema.py

Contains Pydantic schemas for risk management API validation.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel, Field


# ==========================================
# Risk Amount Schema
# ==========================================


class RiskCalculateSchema(BaseModel):
    """
    Schema for calculating risk amount.
    """

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
            "example": 2
        },
    )


# ==========================================
# Forex Lot Size Schema
# ==========================================


class LotSizeSchema(BaseModel):
    """
    Schema for Forex lot size calculation.
    """

    risk_amount: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 200
        },
    )

    stop_loss_pips: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 20
        },
    )

    pip_value: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 10
        },
    )


# ==========================================
# Risk Reward Schema
# ==========================================


class RiskRewardSchema(BaseModel):
    """
    Schema for risk reward calculation.
    """

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
            "example": 1.0980
        },
    )

    take_profit: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 1.1060
        },
    )