class Transaction:

    def __init__(self, transaction_type, account, amount):
        self.transaction_type = transaction_type
        self.account = account
        self.amount = amount

    def show_details(self):
        print("Transaction Type:", self.transaction_type)
        print("Account:", self.account)
        print("Amount:", self.amount)