"""
decision_result.py

Contains decision result model.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from dataclasses import dataclass


@dataclass
class DecisionResult:
    """
    Represents a trading decision result.
    """

    action: str

    confidence: float

    reason: str
