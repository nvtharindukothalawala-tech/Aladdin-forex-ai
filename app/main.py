print("=== Aladdin Forex Risk Calculator ===")

balance = float(input("Enter account balance: "))
risk_percentage = float(input("Enter risk percentage: "))

if balance > 0:
    risk_amount = balance * risk_percentage / 100

    print()
    print("------ Result ------")
    print("Account Balance:", balance)
    print("Risk Percentage:", risk_percentage, "%")
    print("Risk Amount:", risk_amount)
else:
    print("Error: Account balance must be greater than 0.")