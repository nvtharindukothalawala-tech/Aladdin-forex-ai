"""
multi_timeframe_result.py

Stores multi-timeframe market analysis results.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from dataclasses import dataclass


@dataclass
class MultiTimeframeResult:
    """
    Combined market direction across multiple timeframes.
    """

    higher_timeframe_bias: str

    middle_timeframe_bias: str

    entry_timeframe_bias: str

    alignment: str

    confidence: float

    summary: str