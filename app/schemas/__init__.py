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
from app.schemas.analysis_schema import (
    MarketAnalysisRequest,
)
from app.schemas.decision_schema import (
    DecisionRequest,
)
from app.schemas.trading_schema import (
    TradingRequest,
)

__all__ = [
    "AccountCreateSchema",
    "TradeCreateSchema",
    "TradeResponseSchema",
    "TradeCloseSchema",
    "TradeStatisticsSchema",
    "PerformanceSchema",
    "MarketAnalysisRequest",
    "DecisionRequest",
    "TradingRequest",
]
