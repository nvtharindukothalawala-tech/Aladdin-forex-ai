class TradeService:

    def __init__(self, repository):

        self.repository = repository
        self.trades = []

    def load_trades(self):

        self.trades = self.repository.load_trades()

        return self.trades
