"""
main.py

Main entry point for the Aladdin Forex Trading Assistant.

This file connects the main components together:
- Account management
- Trade repository
- Trade service
- Application configuration

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.core.config import settings
from app.core.logger import get_logger
from app.models.account import Account
from app.repositories.trade_repository import TradeRepository
from app.services.account_manager import AccountManager
from app.services.trade_service import TradeService

# Application logger
logger = get_logger(__name__)


def create_accounts():
    """
    Create sample trading accounts.

    Returns:
        AccountManager:
            Manager containing accounts.
    """

    manager = AccountManager()

    # Create sample accounts
    account1 = Account(
        account_id="ACC001",
        balance=5000,
        currency=settings.DEFAULT_CURRENCY,
        leverage=100,
    )

    account2 = Account(
        account_id="ACC002",
        balance=10000,
        currency=settings.DEFAULT_CURRENCY,
        leverage=100,
    )

    account3 = Account(
        account_id="ACC003",
        balance=25000,
        currency=settings.DEFAULT_CURRENCY,
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

    logger.info(
        "%s starting...",
        settings.APP_NAME,
    )

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
            f"Balance: {account.balance} "
            f"{account.currency} | "
            f"Leverage: {account.leverage}"
        )

    # Create trade repository using configuration.
    repository = TradeRepository(settings.TRADES_FILE)

    # Create trade service.
    trade_service = TradeService(repository)

    trades = trade_service.load_trades()

    print(
        "\nTrades Loaded:",
        len(trades),
    )

    logger.info("Application started successfully.")


if __name__ == "__main__":
    main()
