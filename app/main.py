from account import TradingAccount

account = TradingAccount(
    "Main Account",
    5000,
    2
)

print("Before Transactions")
account.show_details()

print()

account.deposit(1000)
account.withdraw(500)

print("After Transactions")
account.show_details()