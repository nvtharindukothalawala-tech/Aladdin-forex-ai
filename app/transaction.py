"""
transaction.py

Contains the Transaction class used by the Aladdin Forex Trading Assistant.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from datetime import datetime


class Transaction:
    """
    Represents a single account transaction.

    This class stores transaction details such as
    deposit or withdrawal information.
    """

    # Used to generate unique transaction IDs.
    next_id = 1

    # ==========================================
    # Constructor
    # ==========================================

    def __init__(self, transaction_type, account, amount):
        """
        Create a new transaction.
        """

        # Validate transaction type.
        if not isinstance(transaction_type, str) or not transaction_type.strip():
            raise ValueError("Transaction type cannot be empty.")

        # Validate amount.
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        # Generate a unique transaction ID.
        self.transaction_id = f"TX{Transaction.next_id:03d}"
        Transaction.next_id += 1

        # Store transaction details.
        self.transaction_type = transaction_type
        self.account = account
        self.amount = amount

        # Record the transaction time.
        self.timestamp = datetime.now().isoformat()

    # ==========================================
    # Display
    # ==========================================

    def show_details(self):
        """
        Display the transaction information.
        """

        print("Transaction ID:", self.transaction_id)
        print("Date & Time:", self.timestamp)
        print("Transaction Type:", self.transaction_type)
        print("Account:", self.account)
        print("Amount:", self.amount)
