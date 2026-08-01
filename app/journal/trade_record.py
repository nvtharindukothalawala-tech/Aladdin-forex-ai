"""
trade_record.py

Stores completed trading records
for AI learning and analysis.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class TradeRecord:
    """
    Represents one completed trade.
    """

    symbol: str

    decision: str

    entry_price: float

    exit_price: float

    profit_loss: float

    confidence: float

    reasoning: str

    created_at: datetime = datetime.utcnow()
