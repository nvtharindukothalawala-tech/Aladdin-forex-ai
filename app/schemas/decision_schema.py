"""
decision_schema.py

Contains Pydantic schemas for
decision API validation.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel, Field


class DecisionRequest(BaseModel):
    """
    Input schema for decision generation.
    """

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