"""
account_schema.py

Contains Pydantic schemas for account data validation.

These schemas prepare the Aladdin Forex Trading Assistant
for future API integration.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel, Field


class AccountCreateSchema(BaseModel):
    """
    Schema used when creating a new trading account.

    It validates account information before
    creating an Account object.
    """

    # Unique account identifier
    account_id: str = Field(
        ...,
        min_length=1,
        json_schema_extra={
            "example": "ACC001"
        },
    )

    # Current account balance
    balance: float = Field(
        ...,
        ge=0,
        json_schema_extra={
            "example": 5000
        },
    )

    # Account currency
    currency: str = Field(
        ...,
        min_length=3,
        json_schema_extra={
            "example": "USD"
        },
    )

    # Trading leverage
    leverage: int = Field(
        ...,
        gt=0,
        json_schema_extra={
            "example": 100
        },
    )