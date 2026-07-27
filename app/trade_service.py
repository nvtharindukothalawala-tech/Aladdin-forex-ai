class TradeService:

    def __init__(self, repository):

        self.repository = repository
        self.trades = []

    def load_trades(self):

        self.trades = self.repository.load_trades()

        return self.trades

    def save_trades(self):
        self.repository.save_trades(self.trades)

    def add_trade(self, trade):
        self.trades.append(trade)

    def find_trade(self, trade_id):
        for trade in self.trades:
            if trade.trade_id == trade_id:
                return trade

        return None
