from datetime import datetime

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

        self.open_time = datetime.now()
        self.close_time = None

    def close_trade(self, exit_price):
        self.exit_price = exit_price
        self.status = "Closed"
        self.close_time = datetime.now()

    def calculate_duration(self):

        if self.close_time is None:
            return None

        duration = self.close_time - self.open_time

        return duration

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

    def get_trade_result(self):

        if self.status != "Closed":
            return "Open"

        profit = self.calculate_profit()

        if profit > 0:
            return "Win"

        if profit < 0:
            return "Loss"

        return "Breakeven"

    def calculate_risk_distance(self):
        risk_distance = abs(self.entry_price - self.stop_loss)
        return risk_distance

    def calculate_reward_distance(self):
        reward_distance = abs(self.take_profit - self.entry_price)
        return reward_distance

    def calculate_risk_reward_ratio(self):

        risk_distance = self.calculate_risk_distance()
        reward_distance = self.calculate_reward_distance()

        if risk_distance == 0:
            return None

        ratio = reward_distance / risk_distance

        return ratio