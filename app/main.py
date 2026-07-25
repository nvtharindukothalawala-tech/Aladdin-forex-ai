from account import TradingAccount
from account_manager import AccountManager
from trade import Trade
from json_manager import JSONManager


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

json_manager = JSONManager(
    "data/trades.json"
)


# =====================================
# Add Accounts
# =====================================

manager.add_account(main_account)
manager.add_account(demo_account)
manager.add_account(funded_account)



# =====================================
# Create Sample Trades
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



trade2 = Trade(
    "GBP/USD",
    "Sell",
    1.2500,
    0.20,
    1.2550,
    1.2400
)

trade2.close_trade(1.2450)



trade3 = Trade(
    "USD/JPY",
    "Buy",
    150.000,
    0.10,
    149.000,
    151.000
)

trade3.close_trade(149.500)



trade4 = Trade(
    "AUD/USD",
    "Buy",
    0.6500,
    0.10,
    0.6450,
    0.6600
)



# =====================================
# Add Trades to Manager
# =====================================

manager.add_trade(trade1)
manager.add_trade(trade2)
manager.add_trade(trade3)
manager.add_trade(trade4)



# =====================================
# Display Trade History
# =====================================

manager.show_all_trades()



# =====================================
# Save Trades to JSON
# =====================================

trade_data = []


trade_data.append(trade1.to_dict())
trade_data.append(trade2.to_dict())
trade_data.append(trade3.to_dict())
trade_data.append(trade4.to_dict())


json_manager.save_data(trade_data)


print("\nTrades saved successfully.")



# =====================================
# Load Trades from JSON
# =====================================

loaded_data = json_manager.load_trades()


print("\n===== Loaded JSON Trades =====")


for trade in loaded_data:
    print(
        trade["trade_id"],
        trade["symbol"],
        trade["status"]
    )



# =====================================
# Rebuild Trade Object Test
# =====================================

loaded_trade = Trade.from_dict(
    loaded_data[0]
)


print("\n===== Rebuilt Trade Object =====")

print("Trade ID:", loaded_trade.trade_id)
print("Symbol:", loaded_trade.symbol)
print("Direction:", loaded_trade.direction)
print("Status:", loaded_trade.status)
print("Profit:", loaded_trade.calculate_profit())