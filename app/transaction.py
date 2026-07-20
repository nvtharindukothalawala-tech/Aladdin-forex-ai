from datetime import datetime

class Transaction:

    def __init__(self, transaction_type, account, amount):
        self.transaction_type = transaction_type
        self.account = account
        self.amount = amount
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def show_details(self):
        print("Date & Time:", self.timestamp)
        print("Transaction Type:", self.transaction_type)
        print("Account:", self.account)
        print("Amount:", self.amount)