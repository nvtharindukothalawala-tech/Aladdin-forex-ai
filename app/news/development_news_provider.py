"""
development_news_provider.py

Provides sample economic calendar data
for Aladdin development and testing.

Author: Tharindu Kothalwala
Project: Aladdin
"""


class DevelopmentNewsProvider:
    """
    Provides controlled sample economic events.

    This provider is used when a paid external
    economic calendar API is not available.

    It is NOT real-time market news.
    """

    def get_calendar(
        self,
        country=None,
        currency=None,
    ):
        """
        Return sample economic calendar events.
        """

        events = [
            {
                "currency": "USD",
                "event": "Non-Farm Payrolls",
                "importance": 3,
                "actual": 220000,
                "forecast": 200000,
            },
            {
                "currency": "EUR",
                "event": "GDP Growth Rate",
                "importance": 2,
                "actual": 0.4,
                "forecast": 0.3,
            },
            {
                "currency": "GBP",
                "event": "Inflation Rate",
                "importance": 2,
                "actual": 2.1,
                "forecast": 2.3,
            },
        ]

        if currency:
            currency = currency.upper()

            events = [
                event
                for event in events
                if event["currency"] == currency
            ]

        return events

    def close(self):
        """
        No persistent connection is used.
        """

        pass