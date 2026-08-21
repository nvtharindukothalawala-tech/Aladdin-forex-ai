"""
technical_analysis_service.py

Connects real market analysis with
Aladdin's Technical Analysis Agent.

Author: Tharindu Kothalawala
Project: Aladdin
"""

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
    """

    def __init__(self):
        """
        Create the required market analysis service.
        """

        self.market_service = (
            MarketAnalysisService()
        )

    def analyze(
        self,
        symbol,
    ):
        """
        Get real market data and perform
        technical analysis.
        """

        # Get real market analysis
        market_signal = (
            self.market_service.analyze(
                symbol=symbol,
            )
        )

        # Convert market trend into
        # the format expected by TechnicalAgent
        if market_signal.trend == "Bullish":

            ema_signal = "BULLISH"

        elif market_signal.trend == "Bearish":

            ema_signal = "BEARISH"

        else:

            ema_signal = "NEUTRAL"

        # Run Technical Analysis Agent
        technical_result = (
            TechnicalAgent.analyze(
                ema_signal=ema_signal,
                rsi_value=market_signal.rsi,
                adx_value=market_signal.adx,
                volatility=market_signal.volatility.upper(),
            )
        )

        return technical_result

    def close(self):
        """
        Close the MetaTrader 5 connection.
        """

        self.market_service.close()