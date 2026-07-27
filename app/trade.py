from datetime import datetime


class Trade:

    trade_counter = 1

    def __init__(
        self, symbol, direction, entry_price, lot_size, stop_loss, take_profit
    ):
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("Symbol cannot be empty.")

        if entry_price <= 0:
            raise ValueError("Entry price must be greater than zero.")

        if stop_loss <= 0:
            raise ValueError("Stop loss must be greater than zero.")

        if take_profit <= 0:
            raise ValueError("Take profit must be greater than zero.")

        if lot_size <= 0:

            raise ValueError("Lot size must be greater than zero.")

        direction = direction.capitalize()

        if direction not in ["Buy", "Sell"]:

            raise ValueError("Direction must be either 'Buy' or 'Sell'.")

        if direction == "Buy":

            if stop_loss >= entry_price:

                raise ValueError(
                    "For a Buy trade, stop loss must be below the entry price."
                )

            if take_profit <= entry_price:

                raise ValueError(
                    "For a Buy trade, take profit must be above the entry price."
                )

        if direction == "Sell":

            if stop_loss <= entry_price:

                raise ValueError(
                    "For a Sell trade, stop loss must be above the entry price."
                )

            if take_profit >= entry_price:

                raise ValueError(
                    "For a Sell trade, take profit must be below the entry price."
                )

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

    @classmethod
    def from_dict(cls, data):

        trade = cls(
            data["symbol"],
            data["direction"],
            data["entry_price"],
            data["lot_size"],
            data["stop_loss"],
            data["take_profit"],
        )

        trade.trade_id = data["trade_id"]

        number = int(trade.trade_id.replace("TRD", ""))

        if number >= cls.trade_counter:

            cls.trade_counter = number + 1

        trade.exit_price = data["exit_price"]

        trade.status = data["status"]

        if data.get("open_time"):

            trade.open_time = datetime.fromisoformat(data["open_time"])

        if data.get("close_time") and data["close_time"] != "None":

            trade.close_time = datetime.fromisoformat(data["close_time"])

        else:

            trade.close_time = None

        trade.strategy = data.get("strategy", "")

        trade.reason = data.get("reason", "")

        trade.emotion = data.get("emotion", "")

        trade.lesson_learned = data.get("lesson_learned", "")

        return trade

    def close_trade(self, exit_price):

        if self.status == "Closed":
            raise ValueError("Trade is already closed.")

        if exit_price <= 0:
            raise ValueError("Exit price must be greater than zero.")

        self.exit_price = exit_price

        self.status = "Closed"

        self.close_time = datetime.now()

    def is_open(self):

        return self.status == "Open"

    def calculate_profit(self):

        if self.exit_price is None:

            return None

        if self.direction == "Buy":

            profit = (self.exit_price - self.entry_price) * self.lot_size

        else:

            profit = (self.entry_price - self.exit_price) * self.lot_size

        return round(profit, 5)

    def calculate_duration(self):

        if self.close_time is None:

            return None

        return self.close_time - self.open_time

    def calculate_risk_distance(self):

        return abs(self.entry_price - self.stop_loss)

    def calculate_reward_distance(self):

        return abs(self.take_profit - self.entry_price)

    def calculate_risk_reward_ratio(self):

        risk = self.calculate_risk_distance()

        reward = self.calculate_reward_distance()

        if risk == 0:

            return None

        ratio = reward / risk

        return round(ratio, 2)

    def get_trade_result(self):

        if self.status != "Closed":

            return "Open"

        profit = self.calculate_profit()

        if profit > 0:

            return "Win"

        if profit < 0:

            return "Loss"

        return "Breakeven"

    def add_journal_entry(self, strategy, reason, emotion, lesson_learned):

        self.strategy = strategy

        self.reason = reason

        self.emotion = emotion

        self.lesson_learned = lesson_learned

        print("Trade journal added successfully.")

    def to_dict(self):

        return {
            "trade_id": self.trade_id,
            "symbol": self.symbol,
            "direction": self.direction,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "lot_size": self.lot_size,
            "status": self.status,
            "open_time": str(self.open_time),
            "close_time": str(self.close_time),
            "strategy": self.strategy,
            "reason": self.reason,
            "emotion": self.emotion,
            "lesson_learned": self.lesson_learned,
        }
