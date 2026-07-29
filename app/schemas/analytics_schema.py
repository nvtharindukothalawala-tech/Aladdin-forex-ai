"""
analytics_schema.py

Contains Pydantic schemas for trade analytics API responses.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel


class TradeStatisticsSchema(BaseModel):
    """
    Schema used for trade performance statistics.
    """

    total_trades: int

    open_trades: int

    winning_trades: int

    losing_trades: int

    win_rate: float

    total_profit: float

    average_profit: float

    profit_factor: float