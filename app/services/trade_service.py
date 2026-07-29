"""
trade_service.py

Contains the TradeService class used by the
Aladdin Forex Trading Assistant.

This service manages trade operations and
records important system events using logging.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.core.logger import get_logger


class TradeService:
    """
    Manage trade-related operations.

    This service keeps trades in memory and uses
    a repository to load and save trade data.

    Logging is used to record important trade events.
    """

    # ==========================================
    # Logger
    # ==========================================

    logger = get_logger(__name__)

    # ==========================================
    # Constructor
    # ==========================================

    def __init__(self, repository):
        """
        Create the trade service.

        Args:
            repository:
                Repository used to load and save trades.
        """

        # Store the repository dependency.
        self.repository = repository

        # Store trades currently loaded into memory.
        self.trades = []

    # ==========================================
    # Data Loading and Saving
    # ==========================================

    def load_trades(self):
        """
        Load trades from the repository.

        Returns:
            list:
                All loaded Trade objects.
        """

        self.trades = self.repository.load_trades()

        self.logger.info(
            "Loaded %s trades successfully.",
            len(self.trades),
        )

        return self.trades

    def save_trades(self):
        """
        Save the current trades using the repository.
        """

        self.repository.save_trades(self.trades)

        self.logger.info(
            "Saved %s trades successfully.",
            len(self.trades),
        )

    # ==========================================
    # Trade Management
    # ==========================================

    def add_trade(self, trade):
        """
        Add a new trade to the in-memory trade list.

        Args:
            trade:
                Trade object that should be added.
        """

        self.trades.append(trade)

        self.logger.info(
            "Trade added successfully: %s",
            trade.trade_id,
        )

    def find_trade(self, trade_id):
        """
        Find a trade using its unique ID.

        Args:
            trade_id:
                Unique ID of the trade.

        Returns:
            Trade:
                Matching Trade object.

            None:
                If no matching trade is found.
        """

        for trade in self.trades:

            if trade.trade_id == trade_id:

                self.logger.info(
                    "Trade found: %s",
                    trade_id,
                )

                return trade

        self.logger.warning(
            "Trade not found: %s",
            trade_id,
        )

        return None
