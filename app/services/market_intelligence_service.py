"""
market_intelligence_service.py

Combines real market technical analysis,
market structure intelligence,
economic news analysis,
multi-timeframe analysis,
and market session analysis.

Author: Tharindu Kothalawala
Project: Aladdin
"""

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

from app.config.instrument_config import (
    normalize_symbol,
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

from app.services.technical_analysis_service import (
    TechnicalAnalysisService,
)

from app.services.news_analysis_service import (
    NewsAnalysisService,
)


class MarketIntelligenceService:
    """
    Combines technical, market structure,
    economic news, multi-timeframe, and
    market session analysis using real
    MetaTrader 5 data and development news data.

    MetaTrader5 is optional during import so
    Linux CI environments can load the project.

    Real MT5 market intelligence still requires
    Windows with MetaTrader5 installed.
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

        self.news_service = (
            NewsAnalysisService()
        )

    # ======================================================
    # MT5 AVAILABILITY
    # ======================================================

    @staticmethod
    def _require_mt5():
        """
        Ensure MetaTrader5 is available before
        requesting real MT5 market analysis.
        """

        if mt5 is None:
            raise RuntimeError(
                "MetaTrader5 is not installed on this platform. "
                "Real market intelligence requires Windows with "
                "the MetaTrader5 Python package installed."
            )

        return mt5

    # ======================================================
    # NEWS CURRENCY
    # ======================================================

    def _get_news_currency(
        self,
        symbol,
    ):
        """
        Determine the currency to use for
        economic news analysis.

        Forex pairs contain two currencies.

        For example:

            EURUSD -> EUR
            GBPUSD -> GBP
            USDJPY -> USD

        For XAUUSD, USD news is used because
        XAU is a metal rather than a currency.
        """

        internal_symbol = normalize_symbol(
            symbol
        )

        if internal_symbol == "XAUUSD":
            return "USD"

        if internal_symbol.endswith("USD"):
            return internal_symbol[:3]

        if internal_symbol.startswith("USD"):
            return "USD"

        return internal_symbol[:3]

    # ======================================================
    # COMPLETE MARKET INTELLIGENCE
    # ======================================================

    def analyze(
        self,
        symbol,
        candle_count=1000,
        lookback=2,
    ):
        """
        Generate complete market intelligence.
        """

        self._require_mt5()

        timeframe_m15 = mt5.TIMEFRAME_M15
        timeframe_h1 = mt5.TIMEFRAME_H1
        timeframe_h4 = mt5.TIMEFRAME_H4

        # ==========================================
        # Entry Timeframe Technical Analysis
        # ==========================================

        entry_timeframe_result = (
            self.technical_service.analyze(
                symbol=symbol,
                timeframe=timeframe_m15,
            )
        )

        # ==========================================
        # Middle Timeframe Technical Analysis
        # ==========================================

        middle_timeframe_result = (
            self.technical_service.analyze(
                symbol=symbol,
                timeframe=timeframe_h1,
            )
        )

        # ==========================================
        # Higher Timeframe Technical Analysis
        # ==========================================

        higher_timeframe_result = (
            self.technical_service.analyze(
                symbol=symbol,
                timeframe=timeframe_h4,
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
                timeframe=timeframe_h1,
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
        # Get Latest H1 Candle
        #
        # Used for market session detection.
        # ==========================================

        candles = (
            self.market_service.provider.get_candles(
                symbol=symbol,
                timeframe=timeframe_h1,
                count=1,
            )
        )

        if not candles:
            raise ValueError(
                f"No market candles available "
                f"for {symbol}."
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
        # Economic News Analysis
        # ==========================================

        news_currency = (
            self._get_news_currency(
                symbol
            )
        )

        news_result = (
            self.news_service.analyze(
                currency=news_currency,
            )
        )

        # ==========================================
        # Combined Market Intelligence
        # ==========================================

        intelligence_result = (
            MarketIntelligenceAgent.analyze(
                technical_result=technical_result,
                news_result=news_result,
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

            "news": news_result,

            "multi_timeframe": timeframe_result,

            "market_session": session_result,

            "intelligence": intelligence_result,
        }

    # ======================================================
    # CLEANUP
    # ======================================================

    def close(self):
        """
        Close MetaTrader 5 and news services.
        """

        self.technical_service.close()

        self.news_service.close()