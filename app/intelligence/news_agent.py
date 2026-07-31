"""
news_agent.py

Forex News Analysis Agent for Aladdin.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.intelligence.news_result import (
    NewsAnalysisResult,
)


class NewsAgent:
    """
    Analyzes economic news impact
    on forex markets.
    """

    @staticmethod
    def analyze(
        currency,
        event_type,
        importance,
        sentiment,
    ):
        """
        Generate forex news analysis.
        """

        confidence = 50

        # Determine impact

        if importance == "HIGH":

            impact = "HIGH"

            confidence += 20

        elif importance == "MEDIUM":

            impact = "MEDIUM"

            confidence += 10

        else:

            impact = "LOW"

        # Determine market effect

        if sentiment == "BULLISH":

            market_effect = f"{currency} strength expected"

            confidence += 10

        elif sentiment == "BEARISH":

            market_effect = f"{currency} weakness expected"

            confidence += 10

        else:

            market_effect = "Limited market impact expected"

        return NewsAnalysisResult(
            currency=currency,
            impact=impact,
            sentiment=sentiment,
            market_effect=market_effect,
            confidence=min(
                confidence,
                100,
            ),
        )
