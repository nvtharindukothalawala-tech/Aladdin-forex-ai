"""
trade_dependencies.py

Contains reusable dependencies for trade-related services.

These dependencies prepare the Aladdin Forex Trading Assistant
for future FastAPI integration.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.core.config import settings
from app.repositories.trade_repository import TradeRepository
from app.services.trade_service import TradeService


def get_trade_repository():
    """
    Create and return a TradeRepository instance.

    Returns:
        TradeRepository:
            Repository used for trade storage.
    """

    return TradeRepository(
        settings.TRADES_FILE
    )


def get_trade_service():
    """
    Create and return a TradeService instance.

    Returns:
        TradeService:
            Service used for trade operations.
    """

    repository = get_trade_repository()

    return TradeService(repository)