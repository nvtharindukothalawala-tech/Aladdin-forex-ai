"""
analysis_schema.py

Contains Pydantic schemas for market analysis API.

Author: Tharindu Kothalawala
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
            "example": 1.1696
        },
    )

    ema: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 1.1687
        },
    )

    rsi: float = Field(
        ...,
        ge=0,
        le=100,
        json_schema_extra={
            "example": 42.06
        },
    )

    atr: float = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 0.001096
        },
    )

    adx: float = Field(
        ...,
        ge=0,
        le=100,
        json_schema_extra={
            "example": 39.59
        },
    )