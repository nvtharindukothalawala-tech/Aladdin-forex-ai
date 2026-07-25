from account import TradingAccount
from account_manager import AccountManager
from trade import Trade
from trade_repository import TradeRepository
from trade_service import TradeService


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
# Or Create Initial Sample Trades
# =====================================

saved_trades = trade_service.load_trades()



if saved_trades:

    print("\nLoading existing trades...")


else:

    print("\nCreating new sample trades...")



    # =====================================
    # Trade 1
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
    # Trade 2
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
    # Trade 3
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
    # Trade 4
    # Open Position
    # =====================================

    trade4 = Trade(
        "AUD/USD",
        "Buy",
        0.6500,
        0.10,
        0.6450,
        0.6600
    )



    # Add new trades to service

    trade_service.add_trade(trade1)
    trade_service.add_trade(trade2)
    trade_service.add_trade(trade3)
    trade_service.add_trade(trade4)



    # Save trades

    trade_service.save_trades()


    print("New trades saved successfully.")




# =====================================
# Sync Service Trades With Manager
# =====================================

for trade in trade_service.trades:

    if trade not in manager.trades:

        manager.add_trade(trade)



# =====================================
# Display Current Trade History
# =====================================

manager.show_all_trades()