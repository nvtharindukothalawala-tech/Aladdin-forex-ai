"""
main.py

Main entry point for the Aladdin Forex Trading Assistant.

This file creates sample trading accounts, loads saved trades,
creates sample trades when needed, and displays trade information.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.account import TradingAccount
from app.account_manager import AccountManager
from app.trade import Trade
from app.trade_repository import TradeRepository
from app.trade_service import TradeService

# ==========================================
# Account Setup
# ==========================================


def create_sample_accounts():
    """
    Create sample trading accounts for demonstration.

    Returns:
        AccountManager: Manager containing the sample accounts.
    """

    account_manager = AccountManager()

    main_account = TradingAccount("Main Account", 5000, 2)
    demo_account = TradingAccount("Demo Account", 10000, 1)
    funded_account = TradingAccount("Funded Account", 25000, 0.5)

    account_manager.add_account(main_account)
    account_manager.add_account(demo_account)
    account_manager.add_account(funded_account)

    return account_manager


# ==========================================
# Sample Trade Setup
# ==========================================


def create_sample_trades():
    """
    Create sample Forex trades for demonstration.

    Returns:
        list: List containing sample Trade objects.
    """

    # Profitable EUR/USD buy trade.
    trade1 = Trade(
        "EUR/USD",
        "Buy",
        1.0800,
        0.10,
        1.0750,
        1.0900,
    )
    trade1.close_trade(1.0850)

    trade1.add_journal_entry(
        "Breakout",
        "Price broke above resistance.",
        "Confident",
        "Wait for candle confirmation.",
    )

    # Profitable GBP/USD sell trade.
    trade2 = Trade(
        "GBP/USD",
        "Sell",
        1.2500,
        0.20,
        1.2550,
        1.2400,
    )
    trade2.close_trade(1.2450)

    # Losing USD/JPY buy trade.
    trade3 = Trade(
        "USD/JPY",
        "Buy",
        150.000,
        0.10,
        149.000,
        151.000,
    )
    trade3.close_trade(149.500)

    # Open AUD/USD buy trade.
    trade4 = Trade(
        "AUD/USD",
        "Buy",
        0.6500,
        0.10,
        0.6450,
        0.6600,
    )

    return [trade1, trade2, trade3, trade4]


# ==========================================
# Display Functions
# ==========================================


def display_accounts(account_manager):
    """
    Display all trading accounts.

    Args:
        account_manager: AccountManager containing the accounts.
    """

    print("\nTrading Accounts")
    print("-" * 40)

    for account in account_manager.get_all_accounts():
        print(
            f"Account: {account.account_id} | "
            f"Balance: ${account.balance:.2f} | "
            f"Risk: {account.risk_percentage}%"
        )


def display_trades(trades):
    """
    Display basic information about all trades.

    Args:
        trades: List of Trade objects.
    """

    print("\nTrade History")
    print("-" * 40)

    if not trades:
        print("No trades are available.")
        return

    for trade in trades:
        profit = trade.calculate_profit()

        # Open trades do not yet have a final profit.
        profit_display = f"{profit:.5f}" if profit is not None else "Not available"

        print(
            f"{trade.symbol} | "
            f"{trade.direction} | "
            f"Status: {trade.status} | "
            f"Profit: {profit_display}"
        )


# ==========================================
# Main Application
# ==========================================


def main():
    """
    Run the Aladdin demonstration application.
    """

    # AccountManager handles only trading accounts.
    account_manager = create_sample_accounts()

    # TradeService handles trade loading, storage, and management.
    trade_repository = TradeRepository("data/trades.json")
    trade_service = TradeService(trade_repository)

    saved_trades = trade_service.load_trades()

    if saved_trades:
        print("\nLoading existing trades...")
    else:
        print("\nCreating new sample trades...")

        sample_trades = create_sample_trades()

        for trade in sample_trades:
            trade_service.add_trade(trade)

        trade_service.save_trades()

        print("New trades saved successfully.")

    display_accounts(account_manager)
    display_trades(trade_service.trades)


if __name__ == "__main__":
    main()
