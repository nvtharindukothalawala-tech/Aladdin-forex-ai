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

            print(f"Trade ID: {trade.trade_id}")
            print("Symbol:", trade.symbol)
            print("Direction:", trade.direction)
            print(f"Entry Price : {trade.entry_price:.5f}")
            print(f"Exit Price  : {trade.exit_price:.5f}")
            print(f"Stop Loss   : {trade.stop_loss:.5f}")
            print(f"Take Profit : {trade.take_profit:.5f}")
            print("Lot Size:", trade.lot_size)
            print("Status:", trade.status)
            print("Trade Result:", trade.get_trade_result())
            print("Open Time:", trade.open_time)
            print("Close Time:", trade.close_time)
            print("Trade Duration:", trade.calculate_duration())

            print(f"Risk Distance: {trade.calculate_risk_distance():.5f}")
            print(f"Reward Distance: {trade.calculate_reward_distance():.5f}")

            risk_reward = trade.calculate_risk_reward_ratio()

            if risk_reward is not None:
                print(f"Risk-to-Reward Ratio: 1:{risk_reward:.2f}")
            else:
                print("Risk-to-Reward Ratio: Invalid")

            profit = trade.calculate_profit()

            if profit is not None:
                print(f"Profit: {profit:.5f}")
            else:
                print("Profit: Not available")

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

    def calculate_gross_profit(self):

        gross_profit = 0

        for trade in self.trades:

            profit = trade.calculate_profit()

            if profit > 0:
                gross_profit += profit

        return gross_profit

    def calculate_gross_loss(self):

        gross_loss = 0

        for trade in self.trades:

            profit = trade.calculate_profit()

            if profit < 0:
                gross_loss += abs(profit)

        return gross_loss

    def calculate_profit_factor(self):

        gross_profit = self.calculate_gross_profit()
        gross_loss = self.calculate_gross_loss()

        if gross_loss == 0:
            return 0

        profit_factor = gross_profit / gross_loss

        return profit_factor

    def calculate_average_winning_trade(self):

        winning_trades = self.count_winning_trades()

        if winning_trades == 0:
            return 0

        gross_profit = self.calculate_gross_profit()

        average_winning_trade = gross_profit / winning_trades

        return average_winning_trade

    def calculate_average_losing_trade(self):

        losing_trades = self.count_losing_trades()

        if losing_trades == 0:
            return 0

        gross_loss = self.calculate_gross_loss()

        average_losing_trade = gross_loss / losing_trades

        return average_losing_trade

    def calculate_risk_reward_ratio(self):

        average_winning_trade = self.calculate_average_winning_trade()
        average_losing_trade = self.calculate_average_losing_trade()

        if average_losing_trade == 0:
            return 0

        risk_reward_ratio = average_winning_trade / average_losing_trade

        return risk_reward_ratio

    def calculate_max_consecutive_wins(self):

        current_wins = 0
        max_wins = 0

        for trade in self.trades:
            profit = trade.calculate_profit()

            if profit > 0:
                current_wins += 1

                if current_wins > max_wins:
                    max_wins = current_wins
            else:
                current_wins = 0

        return max_wins

    def calculate_max_consecutive_losses(self):

        current_losses = 0
        max_losses = 0

        for trade in self.trades:
            profit = trade.calculate_profit()

            if profit < 0:
                current_losses += 1

                if current_losses > max_losses:
                    max_losses = current_losses
            else:
                current_losses = 0

        return max_losses

    def calculate_max_drawdown(self):

        equity = 0
        peak_equity = 0
        max_drawdown = 0

        for trade in self.trades:
            profit = trade.calculate_profit()
            equity += profit

            if equity > peak_equity:
                peak_equity = equity

            drawdown = peak_equity - equity

            if drawdown > max_drawdown:
                max_drawdown = drawdown

        return max_drawdown

    def calculate_max_drawdown_percentage(self, starting_balance):

        max_drawdown = self.calculate_max_drawdown()

        if starting_balance <= 0:
            return 0

        drawdown_percentage = (max_drawdown / starting_balance) * 100

        return drawdown_percentage
    
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
        winning_trades = self.count_winning_trades()
        losing_trades = self.count_losing_trades()
        win_rate = self.calculate_win_rate()

        total_profit = self.calculate_total_profit()
        average_profit = self.calculate_average_profit()

        largest_winning_trade = self.find_largest_winning_trade()
        largest_losing_trade = self.find_largest_losing_trade()

        gross_profit = self.calculate_gross_profit()
        gross_loss = self.calculate_gross_loss()
        profit_factor = self.calculate_profit_factor()

        average_winning_trade = self.calculate_average_winning_trade()
        average_losing_trade = self.calculate_average_losing_trade()
        risk_reward_ratio = self.calculate_risk_reward_ratio()
        max_consecutive_wins = self.calculate_max_consecutive_wins()
        max_consecutive_losses = self.calculate_max_consecutive_losses()
        max_drawdown = self.calculate_max_drawdown()
        max_drawdown_percentage = self.calculate_max_drawdown_percentage(6000)

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
        print(f"Largest Losing Trade  : {largest_losing_trade:.5f}")
        print(f"Gross Profit         : {gross_profit:.5f}")
        print(f"Gross Loss           : {gross_loss:.5f}")
        print(f"Profit Factor        : {profit_factor:.2f}")
        print(f"Average Winning Trade : {average_winning_trade:.5f}")
        print(f"Average Losing Trade  : {average_losing_trade:.5f}")
        print(f"Risk-to-Reward Ratio  : {risk_reward_ratio:.3f}")
        print(f"Max Consecutive Wins  : {max_consecutive_wins}")
        print(f"Max Consecutive Losses : {max_consecutive_losses}")
        print(f"Max Drawdown         : {max_drawdown:.5f}")
        print(f"Max Drawdown Percentage : {max_drawdown_percentage:.5f}%")
        print("========================================")