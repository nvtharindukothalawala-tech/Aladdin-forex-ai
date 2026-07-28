"""
risk.py

Contains simple risk calculation functions used by the
Aladdin Forex Trading Assistant.

Author: Tharindu Kothalwala
Project: Aladdin
"""


def calculate_risk(balance, risk_percentage):
    """
    Calculate the amount of money to risk on a trade.

    Args:
        balance (float): Current account balance.
        risk_percentage (float): Percentage of the balance to risk.

    Returns:
        float: Risk amount.
        None: If the balance is zero or negative.
    """

    # A valid account balance must be greater than zero.
    if balance <= 0:
        return None

    # Calculate the money that can be risked.
    risk_amount = balance * risk_percentage / 100

    return risk_amount
