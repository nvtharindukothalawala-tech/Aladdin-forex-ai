"""
schemas package

Contains Pydantic schemas used for
API data validation.

Author: Tharindu Kothalwala
Project: Aladdin
"""


from app.schemas.account_schema import (
    AccountCreateSchema,
)


from app.schemas.trade_schema import (
    TradeCreateSchema,
    TradeResponseSchema,
)


from app.schemas.trade_close_schema import (
    TradeCloseSchema,
)


from app.schemas.analytics_schema import (
    TradeStatisticsSchema,
)


__all__ = [
    "AccountCreateSchema",
    "TradeCreateSchema",
    "TradeResponseSchema",
    "TradeCloseSchema",
    "TradeStatisticsSchema",
]