class TradingAccount:

    def __init__(self, name, balance, risk):
        self.name = name
        self.balance = balance
        self.risk = risk

    def calculate_risk(self):
        risk_amount = self.balance * self.risk / 100
        return risk_amount

    def deposit(self, amount):
        if amount <= 0:
            return False

        self.balance = self.balance + amount
        return True
    
    def withdraw(self, amount):
        if amount <= 0:
            return False

        if amount > self.balance:
            return False

        self.balance = self.balance - amount
        return True