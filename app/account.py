class TradingAccount:

    def __init__(self, name, balance, risk):
        self.name = name
        self._balance = balance
        self.risk = risk

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            print("Balance cannot be negative.")
            return

        self._balance = value

    def calculate_risk(self):
        risk_amount = self._balance * self.risk / 100
        return risk_amount

    def deposit(self, amount):
        if amount <= 0:
            return False

        self.balance = self.balance + amount
        return True

    def withdraw(self, amount):
        if amount <= 0:
            return False

        if amount > self._balance:
            return False

        self.balance = self.balance - amount
        return True

    def show_details(self):
        print("Account:", self.name)
        print("Balance:", self._balance)
        print("Risk:", self.risk, "%")
        print("Risk Amount:", self.calculate_risk())