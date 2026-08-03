"""
analysis_schema.py

Contains Pydantic schemas for market analysis API.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel, Field


class MarketAnalysisRequest(BaseModel):
    """
    Input schema for market analysis.
    """

    symbol: str = Field(
        ...,
        json_schema_extra={
            "example": "EUR/USD"
        },
    )

    current_price: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 1.0850
        },
    )

    sma: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 1.0800
        },
    )

    rsi: float = Field(
        ...,
        ge=0,
        le=100,
        json_schema_extra={
            "example": 60
        },
    )

    atr: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 0.0015
        },
    )