"""
config.py

Contains application configuration settings
for the Aladdin Forex Trading Assistant.

Author: Tharindu Kothalwala
Project: Aladdin
"""


class Settings:
    """
    Store application-wide configuration values.

    Keeping settings in one place makes the
    application easier to maintain and expand.
    """

    # Application information
    APP_NAME = "Aladdin Forex AI"
    VERSION = "1.0.0"

    # Data storage paths
    TRADES_FILE = "data/trades.json"

    # Default trading settings
    DEFAULT_CURRENCY = "USD"


# Create one shared settings object.
settings = Settings()
