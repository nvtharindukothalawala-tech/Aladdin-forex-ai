"""
trade_repository.py

Contains the TradeRepository class used by the
Aladdin Forex Trading Assistant.

The repository connects the trade service with JSON storage
and records storage operations using logging.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.core.logger import get_logger
from app.models.trade import Trade
from app.repositories.json_manager import JSONManager


class TradeRepository:
    """
    Handle saving and loading Trade objects.

    This class uses JSONManager for file operations.
    It converts between Trade objects and dictionaries.

    Logging is used to record storage activities.
    """

    # ==========================================
    # Logger
    # ==========================================

    logger = get_logger(__name__)

    # ==========================================
    # Constructor
    # ==========================================

    def __init__(self, file_path):
        """
        Create a trade repository.

        Args:
            file_path:
                Path of the JSON file used to store trades.
        """

        # JSONManager handles file reading and writing.
        self.json_manager = JSONManager(file_path)

    # ==========================================
    # Save Trades
    # ==========================================

    def save_trades(self, trades):
        """
        Save a list of Trade objects into JSON storage.

        Args:
            trades:
                List of Trade objects that should be saved.

        Raises:
            Exception:
                If saving fails.
        """

        try:

            # Convert Trade objects into dictionaries.
            trade_data = []

            for trade in trades:
                trade_data.append(trade.to_dict())

            # Save converted data.
            self.json_manager.save_data(trade_data)

            self.logger.info(
                "Saved %s trades to storage.",
                len(trades),
            )

        except Exception as error:

            self.logger.error(
                "Failed to save trades: %s",
                error,
            )

            raise

    # ==========================================
    # Load Trades
    # ==========================================

    def load_trades(self):
        """
        Load trade data from JSON storage.

        Returns:
            list:
                Trade objects created from saved data.

        Raises:
            Exception:
                If loading fails.
        """

        try:

            # Load saved dictionaries.
            saved_data = self.json_manager.load_trades()

            trades = []

            # Convert dictionaries into Trade objects.
            for data in saved_data:

                trade = Trade.from_dict(data)

                trades.append(trade)

            self.logger.info(
                "Loaded %s trades from storage.",
                len(trades),
            )

            return trades

        except Exception as error:

            self.logger.error(
                "Failed to load trades: %s",
                error,
            )

            raise
