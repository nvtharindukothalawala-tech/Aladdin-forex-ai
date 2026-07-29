"""
json_manager.py

Contains the JSONManager class used by the
Aladdin Forex Trading Assistant.

This class handles general JSON file reading and writing.

Author: Tharindu Kothalwala
Project: Aladdin
"""

import json
import os


class JSONManager:
    """
    Read data from and write data to a JSON file.

    This class only handles JSON file operations.
    It does not create Trade, Account, or other objects.
    """

    # ==========================================
    # Constructor
    # ==========================================

    def __init__(self, file_path):
        """
        Create a JSON manager for a specific file.

        Args:
            file_path: Location of the JSON file.
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
            data: Data that can be converted into JSON,
                such as a list or dictionary.
        """

        # Get the folder part of the file path.
        directory = os.path.dirname(self.file_path)

        # Create the folder when it does not already exist.
        # This prevents an error when saving to a new folder.
        if directory:
            os.makedirs(directory, exist_ok=True)

        # Open the file in write mode and save the data.
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    # ==========================================
    # Load Data
    # ==========================================

    def load_data(self):
        """
        Load data from the JSON file.

        Returns:
            The saved JSON data.

            An empty list is returned when the file
            does not exist.
        """

        # Return an empty list when there is no saved file.
        if not os.path.exists(self.file_path):
            return []

        # Open the file in read mode and load its JSON data.
        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def load_trades(self):
        """
        Load saved trade dictionaries.

        Returns:
            list: Trade data stored as dictionaries.

        Note:
            TradeRepository converts these dictionaries
            into Trade objects.
        """

        return self.load_data()
