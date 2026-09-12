"""
technical_analysis_service.py

Connects real market analysis with
Aladdin's Technical Analysis Agent.

Author: Tharindu Kothalawala
Project: Aladdin
"""

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

from app.intelligence.technical_agent import (
    TechnicalAgent,
)

from app.services.market_analysis_service import (
    MarketAnalysisService,
)


class TechnicalAnalysisService:
    """
    Connect real market data with
    the Technical Analysis Agent.

    MetaTrader5 is optional during import so
    Linux CI environments can load the project.

    Real MT5 analysis still requires Windows
    with MetaTrader5 installed.
    """

    def __init__(self):
        """
        Create the required market analysis service.
        """

        self.market_service = (
            MarketAnalysisService()
        )

    # ======================================================
    # MT5 TIMEFRAME
    # ======================================================

    @staticmethod
    def _resolve_timeframe(timeframe):
        """
        Return the requested MT5 timeframe.

        If no timeframe is provided,
        H1 is used by default.
        """

        if timeframe is not None:
            return timeframe

        if mt5 is None:
            raise RuntimeError(
                "MetaTrader5 is not installed on this platform. "
                "Real technical analysis requires Windows with "
                "the MetaTrader5 Python package installed."
            )

        return mt5.TIMEFRAME_H1

    # ======================================================
    # TECHNICAL ANALYSIS
    # ======================================================

    def analyze(
        self,
        symbol,
        timeframe=None,
    ):
        """
        Get real market data for a selected
        timeframe and perform technical analysis.

        If no timeframe is supplied,
        H1 is used by default.
        """

        timeframe = self._resolve_timeframe(
            timeframe
        )

        # ==========================================
        # Get real market analysis
        # ==========================================

        market_signal = (
            self.market_service.analyze(
                symbol=symbol,
                timeframe=timeframe,
            )
        )

        # ==========================================
        # Convert market trend
        # ==========================================

        if market_signal.trend == "Bullish":

            ema_signal = "BULLISH"

        elif market_signal.trend == "Bearish":

            ema_signal = "BEARISH"

        else:

            ema_signal = "NEUTRAL"

        # ==========================================
        # Run Technical Analysis Agent
        # ==========================================

        technical_result = (
            TechnicalAgent.analyze(
                ema_signal=ema_signal,
                rsi_value=market_signal.rsi,
                adx_value=market_signal.adx,
                volatility=(
                    market_signal.volatility.upper()
                ),
            )
        )

        return technical_result

    # ======================================================
    # CLEANUP
    # ======================================================

    def close(self):
        """
        Close the MetaTrader 5 connection.
        """

        self.market_service.close()