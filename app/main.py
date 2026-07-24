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

trade1.add_journal_entry(
    "Breakout",
    "Price broke above resistance.",
    "Confident",
    "Wait for candle confirmation."
)

price_difference1 = trade1.calculate_price_difference()
profit1 = trade1.calculate_profit()
duration1 = trade1.calculate_duration()
result1 = trade1.get_trade_result()
risk_distance1 = trade1.calculate_risk_distance()
reward_distance1 = trade1.calculate_reward_distance()
risk_reward1 = trade1.calculate_risk_reward_ratio()

print("=== First Trade ===")
print("Trade ID:", trade1.trade_id)
print("Symbol:", trade1.symbol)
print("Direction:", trade1.direction)
print("Entry Price:", trade1.entry_price)
print("Exit Price:", trade1.exit_price)
print("Stop Loss:", trade1.stop_loss)
print("Take Profit:", trade1.take_profit)
print("Lot Size:", trade1.lot_size)
print("Status:", trade1.status)
print("Open Time:", trade1.open_time)
print("Close Time:", trade1.close_time)
print("Trade Duration:", duration1)
print("Trade Result:", result1)
print(f"Risk Distance: {risk_distance1:.5f}")
print(f"Reward Distance: {reward_distance1:.5f}")
print(f"Price Difference: {price_difference1:.5f}")
print(f"Profit: {profit1:.5f}")
print(f"Risk-to-Reward Ratio: 1:{risk_reward1:.2f}")
print("Strategy:", trade1.strategy)
print("Reason:", trade1.reason)
print("Emotion:", trade1.emotion)
print("Lesson Learned:", trade1.lesson_learned)


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
duration2 = trade2.calculate_duration()
result2 = trade2.get_trade_result()
risk_distance2 = trade2.calculate_risk_distance()
reward_distance2 = trade2.calculate_reward_distance()
risk_reward2 = trade2.calculate_risk_reward_ratio()

print("\n=== Second Trade ===")
print("Trade ID:", trade2.trade_id)
print("Symbol:", trade2.symbol)
print("Direction:", trade2.direction)
print("Entry Price:", trade2.entry_price)
print("Exit Price:", trade2.exit_price)
print("Stop Loss:", trade2.stop_loss)
print("Take Profit:", trade2.take_profit)
print("Lot Size:", trade2.lot_size)
print("Status:", trade2.status)
print("Open Time:", trade2.open_time)
print("Close Time:", trade2.close_time)
print("Trade Duration:", duration2)
print("Trade Result:", result2)
print(f"Risk Distance: {risk_distance2:.5f}")
print(f"Reward Distance: {reward_distance2:.5f}")
print(f"Price Difference: {price_difference2:.5f}")
print(f"Profit: {profit2:.5f}")
print(f"Risk-to-Reward Ratio: 1:{risk_reward2:.2f}")


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
duration3 = trade3.calculate_duration()
result3 = trade3.get_trade_result()
risk_distance3 = trade3.calculate_risk_distance()
reward_distance3 = trade3.calculate_reward_distance()
risk_reward3 = trade3.calculate_risk_reward_ratio()

print("\n=== Third Trade ===")
print("Trade ID:", trade3.trade_id)
print("Symbol:", trade3.symbol)
print("Direction:", trade3.direction)
print("Entry Price:", trade3.entry_price)
print("Exit Price:", trade3.exit_price)
print("Stop Loss:", trade3.stop_loss)
print("Take Profit:", trade3.take_profit)
print("Lot Size:", trade3.lot_size)
print("Status:", trade3.status)
print("Open Time:", trade3.open_time)
print("Close Time:", trade3.close_time)
print("Trade Duration:", duration3)
print("Trade Result:", result3)
print(f"Risk Distance: {risk_distance3:.5f}")
print(f"Reward Distance: {reward_distance3:.5f}")
print(f"Price Difference: {price_difference3:.5f}")
print(f"Profit: {profit3:.5f}")
print(f"Risk-to-Reward Ratio: 1:{risk_reward3:.2f}")

# =====================================
# Fourth Forex trade - Open trade
# =====================================

trade4 = Trade(
    "AUD/USD",
    "Buy",
    0.6500,
    0.10,
    0.6450,
    0.6600
)

print("\n=== Fourth Trade ===")
print("Trade ID:", trade4.trade_id)
print("Symbol:", trade4.symbol)
print("Direction:", trade4.direction)
print("Entry Price:", trade4.entry_price)
print("Status:", trade4.status)

# Store all trades in the manager
manager.add_trade(trade1)
manager.add_trade(trade2)
manager.add_trade(trade3)
manager.add_trade(trade4)

# Display all stored trades
manager.show_all_trades()

trade_id = input("Enter Trade ID: ")

trade = manager.find_trade(trade_id)

if trade:
    print("\n===== Trade Found =====")
    print("Trade ID:", trade.trade_id)
    print("Symbol:", trade.symbol)
    print("Direction:", trade.direction)
    print("Status:", trade.status)

    profit = trade.calculate_profit()

    if profit is not None:
        print(f"Profit: {profit:.5f}")
    else:
        print("Profit: Trade is still open")
else:
    print("Trade not found.")

close_trade_id = input("\nEnter Trade ID to close: ")
exit_price = float(input("Enter Exit Price: "))

close_success = manager.close_trade_by_id(
    close_trade_id,
    exit_price
)

if close_success:
    closed_trade = manager.find_trade(close_trade_id)

    print("\n===== Closed Trade Details =====")
    print("Trade ID:", closed_trade.trade_id)
    print("Status:", closed_trade.status)
    print(f"Exit Price: {closed_trade.exit_price:.5f}")
    print("Close Time:", closed_trade.close_time)
    print(f"Profit: {closed_trade.calculate_profit():.5f}")

delete_trade_id = input("\nEnter Trade ID to delete: ")
delete_success = manager.delete_trade_by_id(delete_trade_id)    

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

view_journal_trade_id = input(
    "\nEnter Trade ID to view journal: "
)

manager.view_trade_journal(view_journal_trade_id)

# ==========================
# Edit Trade Journal
# ==========================

edit_trade_id = input(
    "\nEnter Trade ID to edit journal: "
)

new_strategy = input("Enter New Strategy: ")
new_reason = input("Enter New Reason: ")
new_emotion = input("Enter New Emotion: ")
new_lesson = input("Enter New Lesson Learned: ")

manager.edit_trade_journal(
    edit_trade_id,
    new_strategy,
    new_reason,
    new_emotion,
    new_lesson
)
print("\nUpdated Journal:")
manager.view_trade_journal(edit_trade_id)

#strategy = input("Enter Strategy: ")
#reason = input("Enter Reason: ")
#emotion = input("Enter Emotion: ")
#lesson_learned = input("Enter Lesson Learned: ")

#journal_success = manager.add_trade_journal(
#    journal_trade_id,
#    strategy,
#    reason,
#    emotion,
#    lesson_learned
#)


