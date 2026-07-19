from account import TradingAccount

account = TradingAccount(
    "Main Account",
    5000,
    2
)

print("Current Balance:", account.balance)

withdraw_success = account.withdraw(1000)

if withdraw_success:
    print("Withdrawal successful")
else:
    print("Withdrawal failed")

print("New Balance:", account.balance)
print("Risk Amount:", account.calculate_risk())