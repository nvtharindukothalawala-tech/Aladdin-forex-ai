"""
schemas package

Contains Pydantic request and response schemas
used by the Aladdin API.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.schemas.account_schema import AccountCreateSchema
from app.schemas.analytics_schema import TradeStatisticsSchema
from app.schemas.performance_schema import PerformanceSchema
from app.schemas.trade_close_schema import TradeCloseSchema
from app.schemas.trade_schema import (
    TradeCreateSchema,
    TradeResponseSchema,
)

__all__ = [
    "AccountCreateSchema",
    "TradeCreateSchema",
    "TradeResponseSchema",
    "TradeCloseSchema",
    "TradeStatisticsSchema",
    "PerformanceSchema",
]
