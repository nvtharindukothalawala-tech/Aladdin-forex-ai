from datetime import datetime


class Trade:

    trade_counter = 1

    def __init__(
        self,
        symbol,
        direction,
        entry_price,
        lot_size,
        stop_loss,
        take_profit
    ):

        # Validate the lot size
        if lot_size <= 0:
            raise ValueError("Lot size must be greater than zero.")

        # Validate direction
        if direction not in ["Buy", "Sell"]:
            raise ValueError("Direction must be either 'Buy' or 'Sell'.")

        # Validate Stop Loss and Take Profit for Buy trades
        if direction == "Buy":
            if stop_loss >= entry_price:
                raise ValueError(
                    "For a Buy trade, stop loss must be below the entry price."
                )

            if take_profit <= entry_price:
                raise ValueError(
                    "For a Buy trade, take profit must be above the entry price."
                )

        # Validate Stop Loss and Take Profit for Sell trades
        if direction == "Sell":
            if stop_loss <= entry_price:
                raise ValueError(
                    "For a Sell trade, stop loss must be above the entry price."
                )

            if take_profit >= entry_price:
                raise ValueError(
                    "For a Sell trade, take profit must be below the entry price."
                )

        # Create a unique trade ID
        self.trade_id = f"TRD{Trade.trade_counter:04d}"
        Trade.trade_counter += 1

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

        self.strategy = ""
        self.reason = ""
        self.emotion = ""
        self.lesson_learned = ""
        
    def close_trade(self, exit_price):

        self.exit_price = exit_price
        self.status = "Closed"
        self.close_time = datetime.now()

    def calculate_price_difference(self):

        if self.exit_price is None:
            return None

        if self.direction == "Buy":
            return self.exit_price - self.entry_price

        if self.direction == "Sell":
            return self.entry_price - self.exit_price

        return None

    def calculate_profit(self):

        price_difference = self.calculate_price_difference()

        if price_difference is None:
            return None

        # Temporary simplified profit calculation
        profit = price_difference * self.lot_size

        return profit

    def calculate_duration(self):

        if self.close_time is None:
            return None

        duration = self.close_time - self.open_time

        return duration

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

        risk_distance = abs(
            self.entry_price - self.stop_loss
        )

        return risk_distance

    def calculate_reward_distance(self):

        reward_distance = abs(
            self.take_profit - self.entry_price
        )

        return reward_distance

    def calculate_risk_reward_ratio(self):

        risk_distance = self.calculate_risk_distance()
        reward_distance = self.calculate_reward_distance()

        if risk_distance == 0:
            return None

        ratio = reward_distance / risk_distance

        return ratio

    def add_journal_entry(self, strategy, reason, emotion, lesson_learned):

        self.strategy = strategy
        self.reason = reason
        self.emotion = emotion
        self.lesson_learned = lesson_learned

        print("Trade journal added successfully.")