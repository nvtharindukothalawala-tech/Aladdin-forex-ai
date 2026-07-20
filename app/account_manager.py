from transaction import Transaction

class AccountManager:
    def __init__(self):
        self.accounts = []
        self.transactions = []

    def add_account(self, account):
        existing_account = self.find_account(account.name)

        if existing_account:
            print("Account already exists.")
            return

        self.accounts.append(account)
        print("Account added successfully.")

    def show_all_accounts(self):
        for account in self.accounts:
            account.show_details()
            print()

    def find_account(self, account_name):
        for account in self.accounts:
            if account.name.lower() == account_name.lower():
                return account

        return None
    
    def remove_account(self, account_name):
        account = self.find_account(account_name)

        if account:
            self.accounts.remove(account)
            print("Account removed successfully.")
            return True

        print("Account not found.")
        return False
    
    def update_balance(self, account_name, new_balance):
        account = self.find_account(account_name)

        if account:
            account.balance = new_balance
            print("Balance updated successfully.")
            return True

        print("Account not found.")
        return False
    
    def deposit_to_account(self, account_name, amount):
        account = self.find_account(account_name)

        if account:
            if account.deposit(amount):
                transaction = Transaction(
                    "Deposit",
                    account_name,
                    amount
                )

                self.transactions.append(transaction)

                print("Deposit successful.")
                return True

        print("Deposit failed.")
        return False
    
    def withdraw_from_account(self, account_name, amount):
        account = self.find_account(account_name)

        if account:
            if account.withdraw(amount):
                transaction = Transaction(
                    "Withdrawal",
                    account_name,
                    amount
                )

                self.transactions.append(transaction)

                print("Withdrawal successful.")
                return True

        print("Withdrawal failed.")
        return False
    
    def show_transaction_history(self):
        print("=== Transaction History ===")

        for transaction in self.transactions:
            transaction.show_details()
            print()
    
    def transfer(self, from_account_name, to_account_name, amount):
        from_account = self.find_account(from_account_name)
        to_account = self.find_account(to_account_name)

        if not from_account:
            print("Sender account not found.")
            return False

        if not to_account:
            print("Receiver account not found.")
            return False

        if from_account.withdraw(amount):
            if to_account.deposit(amount):

                transaction = Transaction(
                    "Transfer",
                    f"{from_account_name} -> {to_account_name}",
                    amount
                )

                self.transactions.append(transaction)

                print("Transfer successful.")
                return True

        print("Transfer failed.")
        return False