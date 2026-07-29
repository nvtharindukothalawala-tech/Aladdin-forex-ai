"""
account_manager.py

Contains the AccountManager class used by the
Aladdin Forex Trading Assistant.

This class manages trading account objects in memory
and records important events using the logging system.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.core.logger import get_logger


class AccountManager:
    """
    Manage a collection of trading accounts.

    The manager can add, find, return, and remove accounts.

    Logging is used to record important actions and errors
    instead of directly printing messages.
    """

    # ==========================================
    # Logger
    # ==========================================

    logger = get_logger(__name__)

    # ==========================================
    # Constructor
    # ==========================================

    def __init__(self):
        """
        Create an empty account manager.
        """

        # Store all Account objects in memory.
        self.accounts = []

    # ==========================================
    # Account Management
    # ==========================================

    def add_account(self, account):
        """
        Add a new account to the manager.

        Args:
            account:
                Account object to add.

        Raises:
            ValueError:
                If the account ID already exists.
        """

        # Account IDs must be unique.
        if self.find_account(account.account_id):

            self.logger.warning(
                "Account ID already exists: %s",
                account.account_id,
            )

            raise ValueError("Account ID already exists.")

        self.accounts.append(account)

        self.logger.info(
            "Account added successfully: %s",
            account.account_id,
        )

    def find_account(self, account_id):
        """
        Find an account using its account ID.

        The comparison is case-insensitive.

        Args:
            account_id:
                ID of the account to search.

        Returns:
            Account object:
                When the account exists.

            None:
                When no account is found.
        """

        for account in self.accounts:

            if account.account_id.lower() == account_id.lower():

                return account

        return None

    def get_all_accounts(self):
        """
        Return all accounts currently stored.

        Returns:
            list:
                List of Account objects.
        """

        return self.accounts

    def remove_account(self, account_id):
        """
        Remove an account using its account ID.

        Args:
            account_id:
                ID of the account to remove.

        Returns:
            True:
                When the account was removed.

            False:
                When the account does not exist.
        """

        account = self.find_account(account_id)

        if account:

            self.accounts.remove(account)

            self.logger.info(
                "Account removed successfully: %s",
                account_id,
            )

            return True

        self.logger.warning(
            "Account not found: %s",
            account_id,
        )

        return False
