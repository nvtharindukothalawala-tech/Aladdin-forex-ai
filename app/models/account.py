"""
account.py

Contains the Account class used by the Aladdin Forex Trading Assistant.

Author: Tharindu Kothalwala
Project: Aladdin
"""


class Account:
    """
    Represents a Forex trading account.

    This class stores account information and
    provides methods to deposit and withdraw money.
    """

    # ==========================================
    # Constructor
    # ==========================================

    def __init__(self, account_id, balance, currency, leverage):
        """Create a new trading account."""

        # Validate account information.
        if not isinstance(account_id, str) or not account_id.strip():
            raise ValueError("Account ID cannot be empty.")

        if balance < 0:
            raise ValueError("Balance cannot be negative.")

        if leverage <= 0:
            raise ValueError("Leverage must be greater than zero.")

        # Store account details.
        self.account_id = account_id
        self.balance = balance
        self.currency = currency
        self.leverage = leverage

    # ==========================================
    # Account Operations
    # ==========================================

    def deposit(self, amount):
        """
        Deposit money into the account.
        """

        # Deposit amount must be positive.
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")

        self.balance += amount

    def withdraw(self, amount):
        """
        Withdraw money from the account.
        """

        # Withdrawal amount must be positive.
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")

        # Prevent the balance from becoming negative.
        if amount > self.balance:
            raise ValueError("Insufficient balance.")

        self.balance -= amount
