"""
json_manager.py

Contains the JSONManager class used by the
Aladdin Forex Trading Assistant.

This class handles JSON file operations
and records storage events using logging.

Author: Tharindu Kothalwala
Project: Aladdin
"""

import json
import os

from app.core.logger import get_logger


class JSONManager:
    """
    Read data from and write data to a JSON file.

    This class only handles JSON file operations.
    It does not create Trade, Account, or other objects.

    Logging is used to record file operations.
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
        Create a JSON manager for a specific file.

        Args:
            file_path:
                Location of the JSON file.
        """

        # Store the file location for future operations.
        self.file_path = file_path

    # ==========================================
    # Save Data
    # ==========================================

    def save_data(self, data):
        """
        Save Python data into the JSON file.

        Args:
            data:
                Data that can be converted into JSON,
                such as a list or dictionary.
        """

        # Get the folder part of the file path.
        directory = os.path.dirname(self.file_path)

        # Create the folder if it does not exist.
        if directory:
            os.makedirs(directory, exist_ok=True)

        # Open the file and save JSON data.
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        self.logger.info(
            "JSON data saved successfully: %s",
            self.file_path,
        )

    # ==========================================
    # Load Data
    # ==========================================

    def load_data(self):
        """
        Load data from the JSON file.

        Returns:
            Saved JSON data.

            Empty list:
                When the file does not exist.
        """

        # Check whether the file exists.
        if not os.path.exists(self.file_path):

            self.logger.warning(
                "JSON file not found: %s",
                self.file_path,
            )

            return []

        # Open the file and load JSON data.
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.logger.info(
            "JSON data loaded successfully: %s",
            self.file_path,
        )

        return data

    # ==========================================
    # Trade Data Loading
    # ==========================================

    def load_trades(self):
        """
        Load saved trade dictionaries.

        Returns:
            list:
                Trade data stored as dictionaries.

        Note:
            TradeRepository converts these dictionaries
            into Trade objects.
        """

        return self.load_data()
