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
                Repository used to load and save trade data.
        """

        # Store repository dependency.
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
                Loaded Trade objects.
        """

        self.trades = self.repository.load_trades()

        self.logger.info(
            "Loaded %s trades successfully.",
            len(self.trades),
        )

        return self.trades

    def save_trades(self):
        """
        Save current trades using the repository.
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

        Duplicate trade IDs are not allowed.

        Args:
            trade:
                Trade object that should be added.

        Raises:
            ValueError:
                If the trade already exists.
        """

        # Check whether the trade already exists.
        existing_trade = self.find_trade(trade.trade_id)

        if existing_trade:

            self.logger.warning(
                "Duplicate trade rejected: %s",
                trade.trade_id,
            )

            raise ValueError("Trade already exists.")

        # Add new trade to memory.
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
                Unique trade identifier.

        Returns:
            Trade:
                Matching trade object.

            None:
                When trade is not found.
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
