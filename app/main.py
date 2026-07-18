from risk import calculate_risk

print("=== Aladdin Forex Risk Calculator ===")

balance = float(input("Enter account balance: "))
risk = float(input("Enter risk percentage: "))

result = calculate_risk(balance, risk)

if result is None:
    print("Error: Invalid account balance.")
else:
    print()
    print("Risk Amount:", result)