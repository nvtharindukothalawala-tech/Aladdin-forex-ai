from account import TradingAccount

account = TradingAccount(
    "Main Account",
    5000,
    2
)

print("Before")
account.show_details()

print()

# Directly changing the balance
account.balance = -100000

print("After")
account.show_details()