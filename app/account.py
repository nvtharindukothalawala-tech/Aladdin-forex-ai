class Account:

    def __init__(self, account_id, balance, currency, leverage):
        if not isinstance(account_id, str) or not account_id.strip():
            raise ValueError("Account ID cannot be empty.")

        if balance < 0:
            raise ValueError("Balance cannot be negative.")

        if leverage <= 0:
            raise ValueError("Leverage must be greater than zero.")

        self.account_id = account_id
        self.balance = balance
        self.currency = currency
        self.leverage = leverage

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")

        self.balance += amount

    def withdraw(self, amount):
        self.balance -= amount
