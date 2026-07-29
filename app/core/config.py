"""
config.py

Contains application configuration settings
for the Aladdin Forex Trading Assistant.

Configuration values are loaded from environment variables.

Author: Tharindu Kothalwala
Project: Aladdin
"""

import os

from dotenv import load_dotenv


# Load values from .env file.
load_dotenv()


class Settings:
    """
    Store application-wide configuration values.

    Values are loaded from environment variables.
    This keeps sensitive and changeable settings
    outside the source code.

    Future improvements:
    - Database configuration
    - Cloud deployment settings
    - Secret management
    """

    # ==========================================
    # Application Information
    # ==========================================

    APP_NAME = os.getenv(
        "APP_NAME",
        "Aladdin Forex AI",
    )

    VERSION = os.getenv(
        "VERSION",
        "1.0.0",
    )

    ENVIRONMENT = os.getenv(
        "ENVIRONMENT",
        "development",
    )

    # ==========================================
    # Logging Configuration
    # ==========================================

    LOG_LEVEL = os.getenv(
        "LOG_LEVEL",
        "INFO",
    )

    # ==========================================
    # Data Storage Configuration
    # ==========================================

    DATA_FOLDER = os.getenv(
        "DATA_FOLDER",
        "data",
    )

    TRADES_FILE = os.getenv(
        "TRADES_FILE",
        "data/trades.json",
    )

    # ==========================================
    # Trading Defaults
    # ==========================================

    DEFAULT_CURRENCY = os.getenv(
        "DEFAULT_CURRENCY",
        "USD",
    )

    DEFAULT_RISK_PERCENT = float(
        os.getenv(
            "DEFAULT_RISK_PERCENT",
            "1.0",
        )
    )

    # ==========================================
    # Database Configuration
    # Future PostgreSQL Integration
    # ==========================================

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        None,
    )


# Create one shared settings object.
settings = Settings()