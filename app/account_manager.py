class AccountManager:
    def __init__(self):
        self.accounts = []

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