"""
schemas package

Contains Pydantic schemas used for
API data validation.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.schemas.account_schema import AccountCreateSchema
from app.schemas.trade_schema import TradeCreateSchema


__all__ = [
    "AccountCreateSchema",
    "TradeCreateSchema",
]