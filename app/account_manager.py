from transaction import Transaction

class AccountManager:
    def __init__(self):
        self.accounts = []
        self.transactions = []
        self.trades = []

    def add_account(self, account):
        existing_account = self.find_account(account.name)

        if existing_account:
            print("Account already exists.")
            return

        self.accounts.append(account)
        print("Account added successfully.")

    def add_trade(self, trade):
        self.trades.append(trade)
        print("Trade added successfully.")

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
    
    def generate_statement(self, account_name):
        account = self.find_account(account_name)

        if not account:
            print("Account not found.")
            return

        print("========== ACCOUNT STATEMENT ==========")
        print("Account:", account.name)
        print("Balance:", account.balance)
        print("Risk:", account.risk, "%")
        print("Risk Amount:", account.calculate_risk())

        total_deposits = 0
        total_withdrawals = 0
        total_transfers = 0
        total_transactions = 0

        for transaction in self.transactions:

            if (
                transaction.transaction_type == "Deposit"
                and transaction.account == account.name
            ):
                total_deposits += transaction.amount

            if (
                transaction.transaction_type == "Withdrawal"
                and transaction.account == account.name
            ):
                total_withdrawals += transaction.amount

            if (
                transaction.transaction_type == "Transfer"
                and transaction.account.startswith(account.name)
            ):
                total_transfers += transaction.amount
            
            if account.name in transaction.account:
                total_transactions += 1

        print("Total Deposits:", total_deposits)
        print("Total Withdrawals:", total_withdrawals)
        print("Total Transfers:", total_transfers)
        print("Total Transactions:", total_transactions)

    def show_all_trades(self):

        print("\n=== Trade History ===")

        for trade in self.trades:
            print("Symbol:", trade.symbol)
            print("Direction:", trade.direction)
            print("Entry Price:", trade.entry_price)
            print("Exit Price:", trade.exit_price)
            print("Lot Size:", trade.lot_size)
            print("Status:", trade.status)
            print("--------------------")

    def count_trades(self):

        total_trades = len(self.trades)

        return total_trades

    def calculate_total_profit(self):

        total_profit = 0

        for trade in self.trades:
            total_profit += trade.calculate_profit()

        return total_profit

    def calculate_average_profit(self):

        total_trades = self.count_trades()

        if total_trades == 0:
            return 0

        total_profit = self.calculate_total_profit()

        average_profit = total_profit / total_trades

        return average_profit

    def find_largest_winning_trade(self):

        largest_profit = 0

        for trade in self.trades:
            profit = trade.calculate_profit()

            if profit > largest_profit:
                largest_profit = profit

        return largest_profit

    def find_largest_losing_trade(self):

        largest_loss = 0

        for trade in self.trades:
            profit = trade.calculate_profit()

            if profit < largest_loss:
                largest_loss = profit

        return largest_loss

    def count_winning_trades(self):

        winning_trades = 0

        for trade in self.trades:
            if trade.calculate_profit() > 0:
                winning_trades += 1

        return winning_trades
    
    def count_losing_trades(self):

        losing_trades = 0

        for trade in self.trades:
            if trade.calculate_profit() < 0:
                losing_trades += 1

        return losing_trades

    def calculate_win_rate(self):

        total_trades = len(self.trades)

        if total_trades == 0:
            return 0

        winning_trades = 0

        for trade in self.trades:
            if trade.calculate_profit() > 0:
                winning_trades += 1

        win_rate = (winning_trades / total_trades) * 100

        return win_rate
    
    def generate_trade_summary(self):

        total_trades = self.count_trades()
        total_profit = self.calculate_total_profit()
        winning_trades = self.count_winning_trades()
        losing_trades = self.count_losing_trades()
        win_rate = self.calculate_win_rate()
        average_profit = self.calculate_average_profit()
        largest_winning_trade = self.find_largest_winning_trade()
        largest_losing_trade = self.find_largest_losing_trade()

        print("\n========================================")
        print("        ALADDIN TRADE SUMMARY")
        print("========================================")
        print("Total Trades      :", total_trades)
        print("Winning Trades    :", winning_trades)
        print("Losing Trades     :", losing_trades)
        print(f"Win Rate          : {win_rate:.2f}%")
        print(f"Total Profit      : {total_profit:.5f}")
        print(f"Average Profit    : {average_profit:.5f}")
        print(f"Largest Winning Trade : {largest_winning_trade:.5f}")
        print(f"Largest Losing Trade : {largest_losing_trade:.5f}")
        print("========================================")