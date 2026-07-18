from risk import calculate_risk

print("=== Aladdin Forex Risk Calculator ===")

balance = float(input("Enter account balance: "))
risk = float(input("Enter risk percentage: "))

result = calculate_risk(balance, risk)

print()
print("Risk Amount:", result)