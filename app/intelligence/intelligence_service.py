"""
intelligence_service.py

Service layer for market intelligence.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.intelligence.technical_agent import (
    TechnicalAgent,
)


from app.intelligence.news_agent import (
    NewsAgent,
)


from app.intelligence.market_structure_agent import (
    MarketStructureAgent,
)


from app.intelligence.market_intelligence import (
    MarketIntelligenceAgent,
)


class IntelligenceService:
    """
    Coordinates multiple intelligence agents.
    """

    @staticmethod
    def analyze_market(
        ema_signal,
        rsi_value,
        adx_value,
        volatility,
        currency,
        event_type,
        importance,
        sentiment,
        price_structure,
        liquidity_sweep,
        order_block,
        fair_value_gap,
    ):
        """
        Generate complete market intelligence.

        Agents:

        1. Technical Agent
        2. News Agent
        3. Market Structure Agent
        4. Market Intelligence Agent
        """

        technical_result = TechnicalAgent.analyze(
            ema_signal=ema_signal,
            rsi_value=rsi_value,
            adx_value=adx_value,
            volatility=volatility,
        )

        news_result = NewsAgent.analyze(
            currency=currency,
            event_type=event_type,
            importance=importance,
            sentiment=sentiment,
        )

        structure_result = MarketStructureAgent.analyze(
            price_structure=price_structure,
            liquidity_sweep=liquidity_sweep,
            order_block=order_block,
            fair_value_gap=fair_value_gap,
        )

        market_result = MarketIntelligenceAgent.analyze(
            technical_result=technical_result,
            news_result=news_result,
            structure_result=structure_result,
        )

        return market_result
