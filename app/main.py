from account import TradingAccount
from account_manager import AccountManager
from trade import Trade

# Create trading account objects
main_account = TradingAccount("Main Account", 5000, 2)
demo_account = TradingAccount("Demo Account", 10000, 1)
funded_account = TradingAccount("Funded Account", 25000, 0.5)


# Create the account manager
manager = AccountManager()


# Add accounts to the manager
manager.add_account(main_account)
manager.add_account(demo_account)
manager.add_account(funded_account)


# Test duplicate account prevention
manager.add_account(demo_account)


# Remove the demo account
manager.remove_account("Demo Account")


# Update the main account balance
manager.update_balance("Main Account", 6500)


# Deposit money and save the transaction
manager.deposit_to_account("Main Account", 1000)


# Withdraw money and save the transaction
manager.withdraw_from_account("Main Account", 500)


# Successful transfer
manager.transfer(
    "Main Account",
    "Funded Account",
    1000
)


# Failed transfer because the balance is not enough
manager.transfer(
    "Main Account",
    "Funded Account",
    100000
)


# Display all transaction records
manager.show_transaction_history()


# Generate the account statement
manager.generate_statement("Main Account")


# =====================================
# First Forex trade
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

price_difference1 = trade1.calculate_price_difference()
profit1 = trade1.calculate_profit()

print("=== First Trade ===")
print("Symbol:", trade1.symbol)
print("Direction:", trade1.direction)
print("Entry Price:", trade1.entry_price)
print("Exit Price:", trade1.exit_price)
print("Stop Loss:", trade1.stop_loss)
print("Take Profit:", trade1.take_profit)
print("Lot Size:", trade1.lot_size)
print("Status:", trade1.status)
print(f"Price Difference: {price_difference1:.5f}")
print(f"Profit: {profit1:.5f}")


# =====================================
# Second Forex trade
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

price_difference2 = trade2.calculate_price_difference()
profit2 = trade2.calculate_profit()

print("\n=== Second Trade ===")
print("Symbol:", trade2.symbol)
print("Direction:", trade2.direction)
print("Entry Price:", trade2.entry_price)
print("Exit Price:", trade2.exit_price)
print("Stop Loss:", trade2.stop_loss)
print("Take Profit:", trade2.take_profit)
print("Lot Size:", trade2.lot_size)
print("Status:", trade2.status)
print(f"Price Difference: {price_difference2:.5f}")
print(f"Profit: {profit2:.5f}")


# =====================================
# Third Forex trade
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

price_difference3 = trade3.calculate_price_difference()
profit3 = trade3.calculate_profit()

print("\n=== Third Trade ===")
print("Symbol:", trade3.symbol)
print("Direction:", trade3.direction)
print("Entry Price:", trade3.entry_price)
print("Exit Price:", trade3.exit_price)
print("Stop Loss:", trade3.stop_loss)
print("Take Profit:", trade3.take_profit)
print("Lot Size:", trade3.lot_size)
print("Status:", trade3.status)
print(f"Price Difference: {price_difference3:.5f}")
print(f"Profit: {profit3:.5f}")

# Store all trades in the manager
manager.add_trade(trade1)
manager.add_trade(trade2)
manager.add_trade(trade3)

# Display all stored trades
manager.show_all_trades()

# Display trade statistics
manager.generate_trade_summary()

# Display all remaining accounts
# manager.show_all_accounts()


# Search for an account using user input
search_name = input("\nEnter account name: ")

found_account = manager.find_account(search_name)

if found_account:
    print("Account found:")
    found_account.show_details()
else:
    print("Account not found.")