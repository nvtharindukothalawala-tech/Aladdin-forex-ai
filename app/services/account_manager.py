"""
account_manager.py

Contains the AccountManager class used by the
Aladdin Forex Trading Assistant.

This class manages trading account objects in memory.

Author: Tharindu Kothalwala
Project: Aladdin
"""


class AccountManager:
    """
    Manage a collection of trading accounts.

    The manager can add, find, return, and remove accounts.
    Each account is identified using a unique account ID.
    """

    # ==========================================
    # Constructor
    # ==========================================

    def __init__(self):
        """
        Create an empty account manager.
        """

        # Store all Account objects in this list.
        self.accounts = []

    # ==========================================
    # Account Management
    # ==========================================

    def add_account(self, account):
        """
        Add a new account to the manager.

        Args:
            account: Account object to add.

        Raises:
            ValueError: If the account ID already exists.
        """

        # Account IDs must be unique.
        if self.find_account(account.account_id):
            raise ValueError("Account ID already exists.")

        self.accounts.append(account)

    def find_account(self, account_id):
        """
        Find an account using its account ID.

        The comparison is case-insensitive.

        Args:
            account_id (str): ID of the account to find.

        Returns:
            Account: Matching account object.
            None: If no matching account exists.
        """

        for account in self.accounts:
            if account.account_id.lower() == account_id.lower():
                return account

        return None

    def get_all_accounts(self):
        """
        Return all accounts currently stored.

        Returns:
            list: List of Account objects.
        """

        return self.accounts

    def remove_account(self, account_id):
        """
        Remove an account using its account ID.

        Args:
            account_id (str): ID of the account to remove.

        Returns:
            bool: True if the account was removed.
            bool: False if the account was not found.
        """

        account = self.find_account(account_id)

        if account:
            self.accounts.remove(account)
            return True

        return False
