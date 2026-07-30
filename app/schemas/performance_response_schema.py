"""
performance_response_schema.py

Schemas for performance analytics API.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel


class PerformanceResponse(BaseModel):
    """
    Performance analytics response.
    """

    total_trades: int

    winning_trades: int

    losing_trades: int

    win_rate: float

    total_profit: float

    average_risk_reward: float
