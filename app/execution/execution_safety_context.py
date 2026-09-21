"""
execution_safety_context.py

Carries deterministic pre-execution safety
information into the execution lifecycle.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExecutionSafetyContext:
    """
    Immutable safety information associated
    with one prepared execution.

    The context contains already-calculated
    trade, risk and broker information.

    It does not fetch market data and does
    not send broker orders.
    """

    trade_setup: dict[str, Any]
    risk: dict[str, Any]
    quote: dict[str, Any]
    symbol_info: dict[str, Any]