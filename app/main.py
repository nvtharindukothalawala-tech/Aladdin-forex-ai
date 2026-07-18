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
    }
]

for account in accounts:
    print("Account:", account["name"])
    print("Balance:", account["balance"])
    print("Risk:", account["risk"], "%")
    print()