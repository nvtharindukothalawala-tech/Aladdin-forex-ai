"""
json_trade_repository.py

Contains the JSONTradeRepository class used by the
Aladdin Forex Trading Assistant.

The repository connects the trade service with JSON storage.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.repositories.json_manager import JSONManager
from app.models.trade import Trade


class JSONTradeRepository:
    """
    Handle saving and loading Trade objects using JSON storage.

    This class uses JSONManager for file operations.
    It also converts between Trade objects and dictionaries.
    """

    # ==========================================
    # Constructor
    # ==========================================

    def __init__(self, file_path):
        """
        Create a JSON trade repository.

        Args:
            file_path: Path of the JSON file used to store trades.
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
            trades: List of Trade objects.
        """

        trade_data = []

        for trade in trades:
            trade_data.append(
                trade.to_dict()
            )

        self.json_manager.save_data(
            trade_data
        )

    # ==========================================
    # Load Trades
    # ==========================================

    def load_trades(self):
        """
        Load trades from JSON storage.

        Returns:
            List of Trade objects.
        """

        saved_data = self.json_manager.load_trades()

        trades = []

        for data in saved_data:
            trade = Trade.from_dict(data)
            trades.append(trade)

        return trades


# ==========================================
# Manual Repository Test
# ==========================================

if __name__ == "__main__":

    repository = JSONTradeRepository(
        "data/trades.json"
    )

    trades = repository.load_trades()

    print("\n===== JSON Repository Test =====")

    for trade in trades:
        print(
            trade.trade_id,
            trade.symbol,
            trade.status
        )