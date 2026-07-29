"""
exceptions.py

Contains custom exception classes used by the
Aladdin Forex Trading Assistant.

Author: Tharindu Kothalwala
Project: Aladdin
"""


class AladdinError(Exception):
    """
    Base exception for all Aladdin application errors.
    """

    pass


class AccountError(AladdinError, ValueError):
    """
    Related to trading account problems.
    """

    pass


class TradeError(AladdinError, ValueError):
    """
    Related to trade operation problems.
    """

    pass


class RiskError(AladdinError, ValueError):
    """
    Related to risk management problems.
    """

    pass
