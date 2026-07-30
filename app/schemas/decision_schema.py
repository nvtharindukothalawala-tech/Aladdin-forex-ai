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
