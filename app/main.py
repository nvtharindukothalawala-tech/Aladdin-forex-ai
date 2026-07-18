def calculate_risk(balance, risk_percentage):
    risk_amount = balance * risk_percentage / 100
    return risk_amount


print("=== Aladdin Forex Risk Calculator ===")

balance = float(input("Enter account balance: "))
risk = float(input("Enter risk percentage: "))

result = calculate_risk(balance, risk)

print()
print("Risk Amount:", result)