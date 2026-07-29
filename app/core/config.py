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

    Future improvements:
    - Environment variables
    - Database configuration
    - Cloud deployment settings
    """

    # ==========================================
    # Application Information
    # ==========================================

    APP_NAME = "Aladdin Forex AI"

    VERSION = "1.0.0"

    ENVIRONMENT = "development"

    # ==========================================
    # Logging Configuration
    # ==========================================

    LOG_LEVEL = "INFO"

    # ==========================================
    # Data Storage Configuration
    # ==========================================

    DATA_FOLDER = "data"

    TRADES_FILE = "data/trades.json"

    # ==========================================
    # Trading Defaults
    # ==========================================

    DEFAULT_CURRENCY = "USD"

    DEFAULT_RISK_PERCENT = 1.0

    # ==========================================
    # Database Configuration
    # Future PostgreSQL Integration
    # ==========================================

    DATABASE_URL = None


# Create one shared settings object.
settings = Settings()
