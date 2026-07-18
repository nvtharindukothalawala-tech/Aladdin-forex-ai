from risk import calculate_risk

accounts = [
    {
        "name": "Main Account",
        "balance": 5000,
        "risk": 2
    },
    {
        "name": "Swing Account",
        "balance": 8000,
        "risk": 1.5
    },
    {
        "name": "Demo Account",
        "balance": 10000,
        "risk": 1
    },
    {
        "name": "Invalid Account",
        "balance": -3000,
        "risk": 2
    }
]

print("=== Aladdin Risk Report ===")
print()

for account in accounts:
    risk_amount = calculate_risk(
        account["balance"],
        account["risk"]
    )

    print("Account:", account["name"])

    if risk_amount is None:
        print("Status: Invalid account balance")
    else:
        print("Balance:", account["balance"])
        print("Risk:", account["risk"], "%")
        print("Risk Amount:", risk_amount)

    print()