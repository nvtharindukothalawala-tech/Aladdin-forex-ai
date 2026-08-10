"""
reasoning_result.py

Stores AI trade explanation output.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from dataclasses import dataclass, field


@dataclass
class TradeReasonResult:
    """
    Explainable AI trading decision result.
    """

    decision: str

    confidence: float

    technical_reasons: list[str] = field(
        default_factory=list
    )

    structure_reasons: list[str] = field(
        default_factory=list
    )

    risk_reasons: list[str] = field(
        default_factory=list
    )

    final_message: str = ""