"""
journal_schema.py

Schemas for journal API responses.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel, ConfigDict


class JournalTradeResponse(BaseModel):
    """
    Response schema for journal trades.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    symbol: str

    direction: str

    result: str

    profit_loss: float

    risk_reward: float