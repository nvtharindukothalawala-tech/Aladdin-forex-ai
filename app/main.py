from risk import calculate_risk

balances = [5000, 8000, 10000, -2000]
risk_percentage = 2

print("=== Risk Calculation for Multiple Accounts ===")

for balance in balances:
    result = calculate_risk(balance, risk_percentage)

    if result is None:
        print("Balance:", balance, "-> Invalid account balance")
    else:
        print("Balance:", balance, "-> Risk Amount:", result)