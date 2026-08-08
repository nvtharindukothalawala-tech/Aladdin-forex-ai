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

from app.intelligence.multi_timeframe_agent import (
    MultiTimeframeAgent,
)

from app.intelligence.market_session_agent import (
    MarketSessionAgent,
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
        higher_timeframe_bias=None,
        middle_timeframe_bias=None,
        entry_timeframe_bias=None,
        hour_utc=None,
    ):
        """
        Generate complete market intelligence.

        Agents:

        1. Technical Agent
        2. News Agent
        3. Market Structure Agent
        4. Multi-Timeframe Agent
        5. Market Session Agent
        6. Market Intelligence Agent
        """

        # ==========================================
        # Technical Analysis
        # ==========================================

        technical_result = TechnicalAgent.analyze(
            ema_signal=ema_signal,
            rsi_value=rsi_value,
            adx_value=adx_value,
            volatility=volatility,
        )

        # ==========================================
        # News Analysis
        # ==========================================

        news_result = NewsAgent.analyze(
            currency=currency,
            event_type=event_type,
            importance=importance,
            sentiment=sentiment,
        )

        # ==========================================
        # Market Structure Analysis
        # ==========================================

        structure_result = MarketStructureAgent.analyze(
            price_structure=price_structure,
            liquidity_sweep=liquidity_sweep,
            order_block=order_block,
            fair_value_gap=fair_value_gap,
        )

        # ==========================================
        # Combined Market Intelligence
        # ==========================================

        market_result = MarketIntelligenceAgent.analyze(
            technical_result=technical_result,
            news_result=news_result,
            structure_result=structure_result,
        )

        # ==========================================
        # Multi-Timeframe Analysis
        # ==========================================

        if (
            higher_timeframe_bias is not None
            and middle_timeframe_bias is not None
            and entry_timeframe_bias is not None
        ):
            timeframe_result = MultiTimeframeAgent.analyze(
                higher_timeframe_bias=higher_timeframe_bias,
                middle_timeframe_bias=middle_timeframe_bias,
                entry_timeframe_bias=entry_timeframe_bias,
            )

            market_result.timeframe_alignment = (
                timeframe_result.alignment
            )

            market_result.timeframe_confidence = (
                timeframe_result.confidence
            )

            market_result.timeframe_summary = (
                timeframe_result.summary
            )

        # ==========================================
        # Market Session Analysis
        # ==========================================

        if hour_utc is not None:
            session_result = MarketSessionAgent.analyze(
                hour_utc=hour_utc,
            )

            market_result.market_session = (
                session_result.session
            )

            market_result.session_activity = (
                session_result.activity_level
            )

            market_result.session_condition = (
                session_result.trading_condition
            )

            market_result.session_summary = (
                session_result.summary
            )

        # ==========================================
        # Return Final Intelligence Result
        # ==========================================

        return market_result