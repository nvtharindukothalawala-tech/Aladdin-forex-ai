"""
journal_schema.py

Schemas for journal API responses.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel


class JournalTradeResponse(BaseModel):
    """
    Response schema for journal trades.
    """

    symbol: str

    direction: str

    result: str

    profit_loss: float

    risk_reward: float

    class Config:
        from_attributes = True
