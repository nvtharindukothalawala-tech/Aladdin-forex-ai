"""
trade.py

Contains the Trade class used by the Aladdin Forex Trading Assistant.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from datetime import datetime

from app.core.exceptions import TradeError
from app.core.logger import get_logger


class Trade:
    """
    Represents a single Forex trade.

    This class stores trade information,
    calculates profit, risk, reward,
    and manages journal entries.

    Trade validation errors use TradeError.
    """

    logger = get_logger(__name__)

    # Used to generate unique trade IDs.
    trade_counter = 1

    # ==========================================
    # Constructor
    # ==========================================

    def __init__(
        self,
        symbol,
        direction,
        entry_price,
        lot_size,
        stop_loss,
        take_profit,
    ):
        """
        Create a new trade and validate the input values.
        """

        # Validate symbol.
        if not isinstance(symbol, str) or not symbol.strip():

            Trade.logger.warning(
                "Invalid trade symbol: %s",
                symbol,
            )

            raise TradeError("Symbol cannot be empty.")

        # Validate prices.
        if entry_price <= 0:

            Trade.logger.warning(
                "Invalid entry price: %s",
                entry_price,
            )

            raise TradeError("Entry price must be greater than zero.")

        if stop_loss <= 0:

            Trade.logger.warning(
                "Invalid stop loss: %s",
                stop_loss,
            )

            raise TradeError("Stop loss must be greater than zero.")

        if take_profit <= 0:

            Trade.logger.warning(
                "Invalid take profit: %s",
                take_profit,
            )

            raise TradeError("Take profit must be greater than zero.")

        # Validate lot size.
        if lot_size <= 0:

            Trade.logger.warning(
                "Invalid lot size: %s",
                lot_size,
            )

            raise TradeError("Lot size must be greater than zero.")

        # Standardize direction.
        direction = direction.capitalize()

        if direction not in ["Buy", "Sell"]:

            Trade.logger.warning(
                "Invalid trade direction: %s",
                direction,
            )

            raise TradeError("Direction must be either 'Buy' or 'Sell'.")

        # Validate Buy trade.
        if direction == "Buy":

            if stop_loss >= entry_price:
                raise TradeError(
                    "For a Buy trade, stop loss must be below the entry price."
                )

            if take_profit <= entry_price:
                raise TradeError(
                    "For a Buy trade, take profit must be above the entry price."
                )

        # Validate Sell trade.
        if direction == "Sell":

            if stop_loss <= entry_price:
                raise TradeError(
                    "For a Sell trade, stop loss must be above the entry price."
                )

            if take_profit >= entry_price:
                raise TradeError(
                    "For a Sell trade, take profit must be below the entry price."
                )

        # Generate a unique trade ID.
        self.trade_id = f"TRD{Trade.trade_counter:04d}"
        Trade.trade_counter += 1

        # Store trade details.
        self.symbol = symbol
        self.direction = direction
        self.entry_price = entry_price
        self.exit_price = None
        self.lot_size = lot_size
        self.stop_loss = stop_loss
        self.take_profit = take_profit

        # Trade status.
        self.status = "Open"

        # Record timestamps.
        self.open_time = datetime.now()
        self.close_time = None

        # Trade journal.
        self.strategy = ""
        self.reason = ""
        self.emotion = ""
        self.lesson_learned = ""

        self.logger.info(
            "Trade created: %s %s %s",
            self.trade_id,
            self.symbol,
            self.direction,
        )

    # ==========================================
    # JSON Deserialization
    # ==========================================

    @classmethod
    def from_dict(cls, data):
        """
        Create a Trade object from saved JSON data.
        """

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

        close_time = data.get("close_time")

        if close_time and close_time != "None":
            trade.close_time = datetime.fromisoformat(close_time)
        else:
            trade.close_time = None

        trade.strategy = data.get("strategy", "")
        trade.reason = data.get("reason", "")
        trade.emotion = data.get("emotion", "")
        trade.lesson_learned = data.get("lesson_learned", "")

        return trade

    # ==========================================
    # Trade Status
    # ==========================================

    def close_trade(self, exit_price):
        """
        Close the trade using the given exit price.
        """

        if self.status == "Closed":
            raise TradeError("Trade is already closed.")

        if exit_price <= 0:
            raise TradeError("Exit price must be greater than zero.")

        self.exit_price = exit_price
        self.status = "Closed"
        self.close_time = datetime.now()

        self.logger.info(
            "Trade closed: %s Exit price: %s",
            self.trade_id,
            exit_price,
        )

    def is_open(self):
        """Return True if the trade is still open."""

        return self.status == "Open"

    def is_closed(self):
        """Return True if the trade has been closed."""

        return self.status == "Closed"

    def is_winning(self):
        """Return True if the trade is profitable."""

        profit = self.calculate_profit()

        return profit is not None and profit > 0

    def is_losing(self):
        """Return True if the trade is losing."""

        profit = self.calculate_profit()

        return profit is not None and profit < 0

    # ==========================================
    # Trade Calculations
    # ==========================================

    def calculate_profit(self):
        """
        Calculate the trade profit.
        """

        if self.exit_price is None:
            return None

        if self.direction == "Buy":
            profit = (self.exit_price - self.entry_price) * self.lot_size

        else:
            profit = (self.entry_price - self.exit_price) * self.lot_size

        return round(profit, 5)

    def calculate_duration(self):
        """
        Calculate how long the trade was open.
        """

        if self.close_time is None:
            return None

        return self.close_time - self.open_time

    def calculate_risk_distance(self):
        """
        Calculate distance between entry price and stop loss.
        """

        return abs(self.entry_price - self.stop_loss)

    def calculate_reward_distance(self):
        """
        Calculate distance between entry price and take profit.
        """

        return abs(self.take_profit - self.entry_price)

    def calculate_risk_reward_ratio(self):
        """
        Calculate risk-to-reward ratio.
        """

        risk = self.calculate_risk_distance()
        reward = self.calculate_reward_distance()

        if risk == 0:
            return None

        return round(reward / risk, 2)

    def get_trade_result(self):
        """
        Return the trade result.
        """

        if self.status != "Closed":
            return "Open"

        profit = self.calculate_profit()

        if profit > 0:
            return "Win"

        if profit < 0:
            return "Loss"

        return "Breakeven"

    # ==========================================
    # Trade Journal
    # ==========================================

    def add_journal_entry(
        self,
        strategy,
        reason,
        emotion,
        lesson_learned,
    ):
        """
        Save journal notes for the trade.
        """

        self.strategy = strategy
        self.reason = reason
        self.emotion = emotion
        self.lesson_learned = lesson_learned

    # ==========================================
    # JSON Serialization
    # ==========================================

    def to_dict(self):
        """
        Convert the trade object into a dictionary.
        """

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
            "open_time": self.open_time.isoformat(),
            "close_time": (self.close_time.isoformat() if self.close_time else None),
            "strategy": self.strategy,
            "reason": self.reason,
            "emotion": self.emotion,
            "lesson_learned": self.lesson_learned,
        }
