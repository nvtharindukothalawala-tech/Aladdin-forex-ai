"""
performance_schema.py

Schema for trade performance analytics.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel


class PerformanceSchema(BaseModel):
    """
    Response model for trade performance.
    """

    total_trades: int

    winning_trades: int

    losing_trades: int

    win_rate: float

    total_profit: float

    average_profit: float

    best_trade: str | None

    worst_trade: str | None
