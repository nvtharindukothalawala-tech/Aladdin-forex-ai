def calculate_risk(balance, risk_percentage):
    if balance <= 0:
        return None

    risk_amount = balance * risk_percentage / 100
    return risk_amount