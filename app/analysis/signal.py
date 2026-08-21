"""
signal.py

Contains trading analysis signal model.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from dataclasses import dataclass


@dataclass
class MarketSignal:
    """
    Represents market analysis result.
    """

    symbol: str

    trend: str

    momentum: str

    volatility: str

    ema: float

    rsi: float

    atr: float

    adx: float

    explanation: str