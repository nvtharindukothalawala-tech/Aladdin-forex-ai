"""
config.py

Contains application configuration settings
for the Aladdin Forex Trading Assistant.

Configuration values are loaded from environment variables.

Author: Tharindu Kothalawala
Project: Aladdin
"""

import os

from dotenv import load_dotenv

# Load values from .env file
load_dotenv()


class Settings:
    """
    Store application-wide configuration values.

    Values are loaded from environment variables.
    This keeps sensitive and changeable settings
    outside the source code.
    """

    # ==========================================
    # Application Information
    # ==========================================

    APP_NAME = os.getenv(
        "APP_NAME",
        "Aladdin Forex AI",
    )

    APP_VERSION = os.getenv(
        "APP_VERSION",
        "1.1.0",
    )

    # Backward compatibility
    VERSION = APP_VERSION

    ENVIRONMENT = os.getenv(
        "ENVIRONMENT",
        "development",
    )

    DEBUG = (
        os.getenv(
            "DEBUG",
            "false",
        ).lower()
        == "true"
    )

    # ==========================================
    # Security Configuration
    # ==========================================

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "development-secret-key",
    )

    JWT_ALGORITHM = os.getenv(
        "JWT_ALGORITHM",
        "HS256",
    )

    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "60",
        )
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
    # ==========================================

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./aladdin.db",
    )

    # ==========================================
    # API Configuration
    # ==========================================

    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "*",
        ).split(",")
        if origin.strip()
    ]

        # ==========================================
    # Economic News Configuration
    # ==========================================

    TRADING_ECONOMICS_API_KEY = os.getenv(
        "TRADING_ECONOMICS_API_KEY",
        "",
    )

    TRADING_ECONOMICS_BASE_URL = os.getenv(
        "TRADING_ECONOMICS_BASE_URL",
        "https://api.tradingeconomics.com",
    )


settings = Settings()

# ==============================================
# Production Security Validation
# ==============================================

if settings.ENVIRONMENT.lower() == "production":

    if settings.SECRET_KEY == "development-secret-key":
        raise RuntimeError(
            "SECRET_KEY must be configured " "when ENVIRONMENT=production."
        )

    if settings.DEBUG:
        raise RuntimeError("DEBUG must be disabled " "when ENVIRONMENT=production.")
