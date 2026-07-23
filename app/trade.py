class Trade:

    def __init__(
        self,
        symbol,
        direction,
        entry_price,
        lot_size,
        stop_loss,
        take_profit
    ):
        self.symbol = symbol
        self.direction = direction
        self.entry_price = entry_price
        self.exit_price = None
        self.lot_size = lot_size
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.status = "Open"

    def close_trade(self, exit_price):
        self.exit_price = exit_price
        self.status = "Closed"

    def calculate_price_difference(self):

        if self.exit_price is None:
            return 0

        if self.direction == "Buy":
            return self.exit_price - self.entry_price

        if self.direction == "Sell":
            return self.entry_price - self.exit_price

        return 0

    def calculate_profit(self):
        price_difference = self.calculate_price_difference()
        return price_difference * self.lot_size