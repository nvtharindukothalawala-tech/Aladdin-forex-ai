"""
news_analysis_service.py

Connects economic calendar data with
Aladdin's News Analysis Agent.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.intelligence.news_agent import (
    NewsAgent,
)

from app.news.economic_news_provider import (
    EconomicNewsProvider,
)

from app.news.development_news_provider import (
    DevelopmentNewsProvider,
)


class NewsAnalysisService:
    """
    Connect economic news data with
    the News Analysis Agent.

    Development mode uses sample news data
    when a paid external API is not available.
    """

    def __init__(
        self,
        use_development_provider=True,
    ):
        """
        Create the appropriate news provider.

        Development provider is used by default
        so Aladdin can run without a paid API.
        """

        if use_development_provider:

            self.provider = (
                DevelopmentNewsProvider()
            )

        else:

            self.provider = (
                EconomicNewsProvider()
            )

    def analyze(
        self,
        currency,
    ):
        """
        Get economic events for a currency
        and analyze the latest relevant event.
        """

        events = self.provider.get_calendar(
            currency=currency,
        )

        if not events:
            raise ValueError(
                f"No economic news found for {currency}."
            )

        event = events[0]

        event_currency = (
            event.get("currency")
            or currency
        )

        event_type = (
            event.get("event")
            or event.get("category")
            or "Economic Event"
        )

        importance_value = (
            event.get("importance")
            or "LOW"
        )

        if isinstance(
            importance_value,
            int,
        ):

            if importance_value >= 3:

                importance = "HIGH"

            elif importance_value == 2:

                importance = "MEDIUM"

            else:

                importance = "LOW"

        else:

            importance = str(
                importance_value
            ).upper()

            if importance not in {
                "HIGH",
                "MEDIUM",
                "LOW",
            }:

                importance = "LOW"

        sentiment = "NEUTRAL"

        actual = event.get("actual")
        forecast = event.get("forecast")

        if (
            actual is not None
            and forecast is not None
        ):

            try:

                actual_value = float(
                    actual
                )

                forecast_value = float(
                    forecast
                )

                if actual_value > forecast_value:

                    sentiment = "BULLISH"

                elif actual_value < forecast_value:

                    sentiment = "BEARISH"

            except (
                TypeError,
                ValueError,
            ):

                sentiment = "NEUTRAL"

        return NewsAgent.analyze(
            currency=event_currency,
            event_type=event_type,
            importance=importance,
            sentiment=sentiment,
        )

    def close(self):
        """
        Close the news provider.
        """

        self.provider.close()