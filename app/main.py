from account import TradingAccount
from account_manager import AccountManager
from trade import Trade
from trade_repository import TradeRepository
from trade_service import TradeService
from trade_analytics import TradeAnalytics


# =====================================
# Create Trading Accounts
# =====================================

main_account = TradingAccount(
    "Main Account",
    5000,
    2
)

demo_account = TradingAccount(
    "Demo Account",
    10000,
    1
)

funded_account = TradingAccount(
    "Funded Account",
    25000,
    0.5
)



# =====================================
# Create Managers
# =====================================

manager = AccountManager()


trade_repository = TradeRepository(
    "data/trades.json"
)


trade_service = TradeService(
    trade_repository
)



# =====================================
# Add Accounts
# =====================================

manager.add_account(main_account)
manager.add_account(demo_account)
manager.add_account(funded_account)



# =====================================
# Load Existing Trades
# Or Create Sample Trades
# =====================================

saved_trades = trade_service.load_trades()


if saved_trades:

    print("\nLoading existing trades...")


    for trade in saved_trades:

        manager.add_trade(trade)



else:

    print("\nCreating new sample trades...")



    # =====================================
    # First Trade
    # =====================================

    trade1 = Trade(
        "EUR/USD",
        "Buy",
        1.0800,
        0.10,
        1.0750,
        1.0900
    )


    trade1.close_trade(1.0850)


    trade1.add_journal_entry(
        "Breakout",
        "Price broke above resistance.",
        "Confident",
        "Wait for candle confirmation."
    )



    # =====================================
    # Second Trade
    # =====================================

    trade2 = Trade(
        "GBP/USD",
        "Sell",
        1.2500,
        0.20,
        1.2550,
        1.2400
    )


    trade2.close_trade(1.2450)



    # =====================================
    # Third Trade
    # =====================================

    trade3 = Trade(
        "USD/JPY",
        "Buy",
        150.000,
        0.10,
        149.000,
        151.000
    )


    trade3.close_trade(149.500)



    # =====================================
    # Fourth Open Trade
    # =====================================

    trade4 = Trade(
        "AUD/USD",
        "Buy",
        0.6500,
        0.10,
        0.6450,
        0.6600
    )



    # Add trades to service

    trade_service.add_trade(trade1)
    trade_service.add_trade(trade2)
    trade_service.add_trade(trade3)
    trade_service.add_trade(trade4)



    # Add trades to manager

    manager.add_trade(trade1)
    manager.add_trade(trade2)
    manager.add_trade(trade3)
    manager.add_trade(trade4)



    # Save trades

    trade_service.save_trades()


    print("New trades saved successfully.")




# =====================================
# Display Trade History
# =====================================

manager.show_all_trades()

print("\n===== CREATE TRADE TEST =====")


new_trade = trade_service.create_trade(
    "GBP/JPY",
    "Buy",
    200.50,
    0.10,
    199.50,
    202.00
)


print(
    new_trade.trade_id,
    new_trade.symbol,
    new_trade.status
)

print("\n===== CLOSE TRADE TEST =====")


trade_service.close_trade(
    "TRD0005",
    201.50
)


closed_trade = trade_service.find_trade(
    "TRD0005"
)


print(
    closed_trade.trade_id,
    closed_trade.status,
    closed_trade.exit_price
)

print("\n===== DELETE TRADE TEST =====")


trade_service.delete_trade(
    "TRD0006"
)

print("\n===== UPDATE TRADE TEST =====")


trade_service.update_trade(
    "TRD0004",
    stop_loss=0.6480,
    take_profit=0.6650
)


updated_trade = trade_service.find_trade(
    "TRD0004"
)


print(
    updated_trade.trade_id,
    updated_trade.stop_loss,
    updated_trade.take_profit
)

print("\n===== TRADE ANALYTICS TEST =====")


analytics = TradeAnalytics(
    manager.trades
)


print(
    "Total Trades:",
    analytics.total_trades()
)


print(
    "Winning Trades:",
    analytics.winning_trades()
)


print(
    "Losing Trades:",
    analytics.losing_trades()
)


print(
    "Open Trades:",
    analytics.open_trades()
)


print(
    "Win Rate:",
    analytics.win_rate()
)


print(
    "Total Profit:",
    f"{analytics.total_profit():.5f}"
)


print(
    "Average Profit:",
    f"{analytics.average_profit():.5f}"
)

print(
    "Gross Profit:",
    f"{analytics.gross_profit():.5f}"
)


print(
    "Gross Loss:",
    f"{analytics.gross_loss():.5f}"
)


print(
    "Profit Factor:",
    f"{analytics.profit_factor():.2f}"
)