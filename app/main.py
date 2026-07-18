print("=== Trade Permission Checker ===")

balance = float(input("Enter account balance: "))
risk = float(input("Enter risk percentage: "))

if balance > 0 and risk <= 2:
    print("Trade Allowed")
else:
    print("Trade Not Allowed")