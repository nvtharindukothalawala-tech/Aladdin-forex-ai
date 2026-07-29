"""
main.py

Main entry point for the Aladdin Forex Trading Assistant.

This file connects the main components together:
- Account management
- Trade repository
- Trade service

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.models.account import Account
from app.services.account_manager import AccountManager
from app.repositories.trade_repository import TradeRepository
from app.services.trade_service import TradeService


def create_accounts():
    """
    Create sample trading accounts.

    Returns:
        AccountManager: Manager containing accounts.
    """

    manager = AccountManager()

    # Create sample accounts
    account1 = Account(
        account_id="ACC001",
        balance=5000,
        currency="USD",
        leverage=100,
    )

    account2 = Account(
        account_id="ACC002",
        balance=10000,
        currency="USD",
        leverage=100,
    )

    account3 = Account(
        account_id="ACC003",
        balance=25000,
        currency="USD",
        leverage=50,
    )

    # Add accounts to manager
    manager.add_account(account1)
    manager.add_account(account2)
    manager.add_account(account3)

    return manager


def main():
    """
    Start Aladdin application.
    """

    print("=" * 40)
    print("       ALADDIN FOREX AI")
    print("    Trading Assistant System")
    print("=" * 40)

    # Create accounts
    account_manager = create_accounts()

    print("\nAccounts:")

    for account in account_manager.get_all_accounts():
        print(
            f"{account.account_id} | "
            f"Balance: {account.balance} {account.currency} | "
            f"Leverage: {account.leverage}"
        )

    # Create trade service
    repository = TradeRepository("data/trades.json")

    trade_service = TradeService(repository)

    trades = trade_service.load_trades()

    print("\nTrades Loaded:", len(trades))


if __name__ == "__main__":
    main()
