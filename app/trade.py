class Trade:

    def __init__(self, symbol, direction, entry_price, lot_size):
        self.symbol = symbol
        self.direction = direction
        self.entry_price = entry_price

        self.exit_price = None
        self.lot_size = lot_size
        self.status = "Open"

    def close_trade(self, exit_price):
        self.exit_price = exit_price
        self.status = "Closed"

    def calculate_price_difference(self):
        return self.exit_price - self.entry_price