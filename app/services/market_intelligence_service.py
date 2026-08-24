"""
market_intelligence_service.py

Combines real market technical analysis,
market structure intelligence,
multi-timeframe analysis,
and market session analysis.

Author: Tharindu Kothalawala
Project: Aladdin
"""

import MetaTrader5 as mt5

from app.intelligence.market_intelligence import (
    MarketIntelligenceAgent,
)

from app.intelligence.multi_timeframe_agent import (
    MultiTimeframeAgent,
)

from app.intelligence.market_session_agent import (
    MarketSessionAgent,
)

from app.services.technical_analysis_service import (
    TechnicalAnalysisService,
)


class MarketIntelligenceService:
    """
    Combines technical, market structure,
    multi-timeframe, and market session analysis
    using real MetaTrader 5 data.
    """

    def __init__(self):
        """
        Create required analysis services.
        """

        self.technical_service = (
            TechnicalAnalysisService()
        )

        self.market_service = (
            self.technical_service.market_service
        )

    def analyze(
        self,
        symbol,
        candle_count=1000,
        lookback=2,
    ):
        """
        Generate complete market intelligence.
        """

        # ==========================================
        # Entry Timeframe Technical Analysis
        # ==========================================

        entry_timeframe_result = (
            self.technical_service.analyze(
                symbol=symbol,
                timeframe=mt5.TIMEFRAME_M15,
            )
        )

        # ==========================================
        # Middle Timeframe Technical Analysis
        # ==========================================

        middle_timeframe_result = (
            self.technical_service.analyze(
                symbol=symbol,
                timeframe=mt5.TIMEFRAME_H1,
            )
        )

        # ==========================================
        # Higher Timeframe Technical Analysis
        # ==========================================

        higher_timeframe_result = (
            self.technical_service.analyze(
                symbol=symbol,
                timeframe=mt5.TIMEFRAME_H4,
            )
        )

        # ==========================================
        # Main Technical Analysis
        #
        # H1 is used as the primary timeframe.
        # ==========================================

        technical_result = (
            middle_timeframe_result
        )

        # ==========================================
        # Market Structure Analysis
        #
        # Structure remains on H1.
        # ==========================================

        structure_result = (
            self.market_service.analyze_structure(
                symbol=symbol,
                timeframe=mt5.TIMEFRAME_H1,
                candle_count=candle_count,
                lookback=lookback,
            )
        )

        # ==========================================
        # Multi-Timeframe Analysis
        # ==========================================

        timeframe_result = (
            MultiTimeframeAgent.analyze(
                higher_timeframe_bias=(
                    higher_timeframe_result.trend
                ),
                middle_timeframe_bias=(
                    middle_timeframe_result.trend
                ),
                entry_timeframe_bias=(
                    entry_timeframe_result.trend
                ),
            )
        )

        # ==========================================
        # Get latest H1 candle
        #
        # Used for market session detection.
        # ==========================================

        candles = self.market_service.provider.get_candles(
            symbol=symbol,
            timeframe=mt5.TIMEFRAME_H1,
            count=1,
        )

        if not candles:
            raise ValueError(
                f"No market candles available for {symbol}."
            )

        latest_candle = candles[-1]

        # ==========================================
        # Market Session Analysis
        # ==========================================

        session_result = (
            MarketSessionAgent.analyze(
                hour_utc=latest_candle.timestamp.hour,
            )
        )

        # ==========================================
        # Combined Market Intelligence
        # ==========================================
        #
        # News analysis is not connected yet.
        # Therefore the final intelligence service
        # must handle unavailable news safely.
        # ==========================================

        intelligence_result = (
            MarketIntelligenceAgent.analyze(
                technical_result=technical_result,
                news_result=None,
                structure_result=structure_result,
            )
        )

        # ==========================================
        # Add Multi-Timeframe Information
        # ==========================================

        intelligence_result.timeframe_alignment = (
            timeframe_result.alignment
        )

        intelligence_result.timeframe_confidence = (
            timeframe_result.confidence
        )

        intelligence_result.timeframe_summary = (
            timeframe_result.summary
        )

        # ==========================================
        # Add Market Session Information
        # ==========================================

        intelligence_result.market_session = (
            session_result.session
        )

        intelligence_result.session_activity = (
            session_result.activity_level
        )

        intelligence_result.session_condition = (
            session_result.trading_condition
        )

        intelligence_result.session_summary = (
            session_result.summary
        )

        # ==========================================
        # Return Complete Intelligence
        # ==========================================

        return {
            "symbol": symbol,

            "technical": technical_result,

            "market_structure": structure_result,

            "multi_timeframe": timeframe_result,

            "market_session": session_result,

            "intelligence": intelligence_result,
        }

    def close(self):
        """
        Close MetaTrader 5 connections.
        """

        self.technical_service.close()