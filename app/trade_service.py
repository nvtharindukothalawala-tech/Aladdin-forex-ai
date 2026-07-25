from trade import Trade

class TradeService:

    def __init__(self, repository):

        self.repository = repository
        self.trades = []


    def load_trades(self):

        self.trades = self.repository.load_trades()

        return self.trades


    def add_trade(self, trade):

        self.trades.append(trade)

        print("Trade added successfully.")


    def find_trade(self, trade_id):

        for trade in self.trades:

            if trade.trade_id == trade_id:

                return trade

        return None


    def save_trades(self):

        self.repository.save_trades(
            self.trades
        )

        print("Trades saved successfully.")

    def create_trade(
        self,
        symbol,
        direction,
        entry_price,
        lot_size,
        stop_loss,
        take_profit
    ):

        trade = Trade(
            symbol,
            direction,
            entry_price,
            lot_size,
            stop_loss,
            take_profit
        )

        self.trades.append(trade)

        self.save_trades()

        print("New trade created successfully.")

        return trade

    def close_trade(self, trade_id, exit_price):

        trade = self.find_trade(trade_id)

        if not trade:
            print("Trade not found.")
            return False


        trade.close_trade(exit_price)

        self.save_trades()

        print("Trade closed successfully.")

        return True

    def delete_trade(self, trade_id):

        trade = self.find_trade(trade_id)

        if not trade:
            print("Trade not found.")
            return False


        self.trades.remove(trade)

        self.save_trades()

        print("Trade deleted successfully.")

        return True