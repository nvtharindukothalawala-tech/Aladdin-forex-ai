"""
economic_news_provider.py

Provides economic calendar data for Aladdin.

Author: Tharindu Kothalawala
Project: Aladdin
"""

import requests

from app.core.config import settings


class EconomicNewsProvider:
    """
    Retrieves economic calendar events
    from Trading Economics.
    """

    def __init__(self):
        """
        Initialize the economic news provider.
        """

        self.base_url = (
            settings.TRADING_ECONOMICS_BASE_URL
        )

        self.api_key = (
            settings.TRADING_ECONOMICS_API_KEY
        )

    def get_calendar(
        self,
        country=None,
        currency=None,
    ):
        """
        Retrieve economic calendar events.

        Args:
            country:
                Optional country filter.

            currency:
                Optional currency filter.

        Returns:
            List of economic events.
        """

        if not self.api_key:
            raise RuntimeError(
                "Trading Economics API key is not configured."
            )

        url = (
            f"{self.base_url}/calendar"
        )

        params = {
            "c": self.api_key,
        }

        if country:
            params["country"] = country

        if currency:
            params["currency"] = currency

        response = requests.get(
            url,
            params=params,
            timeout=10,
        )

        if response.status_code != 200:
            raise RuntimeError(
                "Economic news API request failed: "
                f"{response.status_code}"
            )

        data = response.json()

        if not isinstance(data, list):
            raise RuntimeError(
                "Economic news API returned "
                "an unexpected response."
            )

        return data