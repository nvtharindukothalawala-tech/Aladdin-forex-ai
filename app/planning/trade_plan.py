"""
trade_plan.py

Contains TradePlan model.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from dataclasses import dataclass


@dataclass
class TradePlan:
    """
    Represents a planned trade setup.
    """

    symbol: str

    direction: str

    entry_price: float

    stop_loss: float

    take_profit: float

    risk_reward: float
