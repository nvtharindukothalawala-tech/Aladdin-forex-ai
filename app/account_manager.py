class AccountManager:
    def __init__(self):
        self.accounts = []

    def add_account(self, account):
        if self.find_account(account.account_id):
            raise ValueError("Account ID already exists.")

        self.accounts.append(account)

    def find_account(self, account_id):
        for account in self.accounts:
            if account.account_id.lower() == account_id.lower():
                return account

        return None

    def get_all_accounts(self):
        return self.accounts

    def remove_account(self, account_id):
        account = self.find_account(account_id)

        if account:
            self.accounts.remove(account)
            print("Account removed successfully.")
            return True

        print("Account not found.")
        return False
