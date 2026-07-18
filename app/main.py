from account import TradingAccount

account = TradingAccount(
    "Main Account",
    5000,
    2
)

print("Account:", account.name)
print("Balance:", account.balance)
print("Risk:", account.risk, "%")