"""
analysis_schema.py

Contains Pydantic schemas for market analysis API.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from pydantic import BaseModel, Field, model_validator


class MarketAnalysisRequest(BaseModel):
    """
    Input schema for market analysis.

    Supports both the current EMA/ADX inputs and
    older SMA-only requests.
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

    # Current API input
    ema: float | None = Field(
        default=None,
        gt=0,
        json_schema_extra={
            "example": 1.1687
        },
    )

    # Backward-compatible input
    sma: float | None = Field(
        default=None,
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

    # ADX is optional for backward compatibility.
    adx: float | None = Field(
        default=None,
        ge=0,
        le=100,
        json_schema_extra={
            "example": 39.59
        },
    )

    @model_validator(mode="after")
    def validate_moving_average(self):
        """
        Require at least one moving-average value.

        The API accepts either EMA or the older SMA field.
        """

        if self.ema is None and self.sma is None:
            raise ValueError(
                "Either ema or sma must be provided."
            )

        return self