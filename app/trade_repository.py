"""
trade_repository.py

Contains the TradeRepository class used by the
Aladdin Forex Trading Assistant.

The repository connects the trade service with JSON storage.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.json_manager import JSONManager
from app.trade import Trade


class TradeRepository:
    """
    Handle saving and loading Trade objects.

    This class uses JSONManager for file operations.
    It also converts between Trade objects and dictionaries.
    """

    # ==========================================
    # Constructor
    # ==========================================

    def __init__(self, file_path):
        """
        Create a trade repository.

        Args:
            file_path: Path of the JSON file used to store trades.
        """

        # JSONManager handles the actual file reading and writing.
        self.json_manager = JSONManager(file_path)

    # ==========================================
    # Save Trades
    # ==========================================

    def save_trades(self, trades):
        """
        Save a list of Trade objects into the JSON file.

        Args:
            trades: List of Trade objects that should be saved.
        """

        # Convert every Trade object into a dictionary.
        trade_data = []

        for trade in trades:
            trade_data.append(trade.to_dict())

        # Send the converted data to JSONManager.
        self.json_manager.save_data(trade_data)

    # ==========================================
    # Load Trades
    # ==========================================

    def load_trades(self):
        """
        Load trade data from the JSON file.

        Returns:
            list: Trade objects created from the saved JSON data.
        """

        # Load saved dictionaries from the JSON file.
        saved_data = self.json_manager.load_trades()

        trades = []

        # Convert each saved dictionary into a Trade object.
        for data in saved_data:
            trade = Trade.from_dict(data)
            trades.append(trade)

        return trades


# ==========================================
# Manual Repository Test
# ==========================================

if __name__ == "__main__":
    # This code runs only when this file is executed directly.
    repository = TradeRepository("data/trades.json")

    trades = repository.load_trades()

    print("\n===== Repository Test =====")

    for trade in trades:
        print(trade.trade_id, trade.symbol, trade.status)
