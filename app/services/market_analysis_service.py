"""
market_analysis_service.py

Connects MetaTrader 5 market data with
Aladdin technical analysis.

Author: Tharindu Kothalawala
Project: Aladdin
"""

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

from app.analysis.market_analyzer import MarketAnalyzer
from app.market.indicators import TechnicalIndicators
from app.market.mt5_provider import MT5DataProvider
from app.services.market_structure_service import (
    MarketStructureService,
)
from app.intelligence.market_structure_agent import (
    MarketStructureAgent,
)


class MarketAnalysisService:
    """
    Provides complete market analysis using
    real MetaTrader 5 market data.

    The MetaTrader5 package is optional during
    import so Linux CI environments can load and
    test the Aladdin project.

    Real MT5 analysis still requires Windows with
    MetaTrader5 installed.
    """

    def __init__(self):
        """
        Create the market analysis service.
        """

        self.provider = MT5DataProvider()

    # ======================================================
    # MT5 TIMEFRAME
    # ======================================================

    @staticmethod
    def _resolve_timeframe(timeframe):
        """
        Return the requested MT5 timeframe.

        If no timeframe is supplied, use H1.

        The MT5 package is checked only when a real
        market analysis operation is requested.
        """

        if timeframe is not None:
            return timeframe

        if mt5 is None:
            raise RuntimeError(
                "MetaTrader5 is not installed on this platform. "
                "Real MT5 market analysis requires Windows with "
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
        candle_count=1000,
    ):
        """
        Get market data and perform technical analysis.

        Args:
            symbol:
                MT5 symbol, for example EURUSD.

            timeframe:
                MT5 timeframe.

                If not supplied, H1 is used.

            candle_count:
                Number of candles used for analysis.

        Returns:
            MarketSignal containing the analysis.
        """

        timeframe = self._resolve_timeframe(
            timeframe
        )

        candles = self.provider.get_candles(
            symbol=symbol,
            timeframe=timeframe,
            count=candle_count,
        )

        if not candles:
            raise ValueError(
                f"No market candles available for {symbol}."
            )

        prices = [
            candle.close_price
            for candle in candles
        ]

        # ==========================================
        # Technical Indicators
        # ==========================================

        ema = TechnicalIndicators.calculate_ema(
            prices,
            20,
        )

        rsi = TechnicalIndicators.calculate_rsi(
            prices,
            14,
        )

        atr = TechnicalIndicators.calculate_atr(
            candles,
            14,
        )

        adx = TechnicalIndicators.calculate_adx(
            candles,
            14,
        )

        # ==========================================
        # Latest Closing Price
        # ==========================================

        current_price = (
            candles[-1].close_price
        )

        # ==========================================
        # Generate Market Signal
        # ==========================================

        signal = MarketAnalyzer.analyze(
            symbol=symbol,
            current_price=current_price,
            ema=ema,
            rsi=rsi,
            atr=atr,
            adx=adx,
        )

        return signal

    # ======================================================
    # MARKET STRUCTURE ANALYSIS
    # ======================================================

    def analyze_structure(
        self,
        symbol,
        timeframe=None,
        candle_count=1000,
        lookback=2,
    ):
        """
        Analyze market structure using
        real MetaTrader 5 candle data.

        Detects:

        - Swing Highs
        - Swing Lows
        - BOS
        - CHoCH
        - Liquidity Sweep
        - Order Block
        - Fair Value Gap
        """

        timeframe = self._resolve_timeframe(
            timeframe
        )

        candles = self.provider.get_candles(
            symbol=symbol,
            timeframe=timeframe,
            count=candle_count,
        )

        if not candles:
            raise ValueError(
                f"No market candles available for {symbol}."
            )

        # ==========================================
        # Swing Points
        # ==========================================

        swing_highs = (
            MarketStructureService.find_swing_highs(
                candles,
                lookback=lookback,
            )
        )

        swing_lows = (
            MarketStructureService.find_swing_lows(
                candles,
                lookback=lookback,
            )
        )

        # ==========================================
        # Break of Structure
        # ==========================================

        bos = MarketStructureService.detect_bos(
            candles,
            swing_highs,
            swing_lows,
        )

        # ==========================================
        # Change of Character
        # ==========================================

        choch = MarketStructureService.detect_choch(
            candles,
            swing_highs,
            swing_lows,
            bos,
        )

        # ==========================================
        # Liquidity Sweep
        # ==========================================

        liquidity_sweep = (
            MarketStructureService.detect_liquidity_sweep(
                candles,
                swing_highs,
                swing_lows,
            )
        )

        # ==========================================
        # Order Block
        # ==========================================

        order_block = (
            MarketStructureService.detect_order_block(
                candles,
                bos,
            )
        )

        # ==========================================
        # Fair Value Gap
        # ==========================================

        fvg = MarketStructureService.detect_fvg(
            candles,
        )

        # ==========================================
        # Convert BOS / CHoCH to Structure Input
        # ==========================================

        if choch is not None:

            price_structure = "CHOCH"

        elif bos is not None:

            price_structure = bos["type"]

        else:

            price_structure = "RANGE"

        # ==========================================
        # Convert Liquidity Sweep
        # ==========================================

        has_liquidity_sweep = (
            liquidity_sweep is not None
        )

        # ==========================================
        # Convert Order Block
        # ==========================================

        if order_block is not None:

            if (
                order_block["type"]
                == "ORDER_BLOCK_BULLISH"
            ):

                order_block_direction = (
                    "BULLISH"
                )

            elif (
                order_block["type"]
                == "ORDER_BLOCK_BEARISH"
            ):

                order_block_direction = (
                    "BEARISH"
                )

            else:

                order_block_direction = (
                    "NONE"
                )

        else:

            order_block_direction = "NONE"

        # ==========================================
        # Fair Value Gap Status
        # ==========================================

        has_fvg = (
            fvg is not None
        )

        # ==========================================
        # Generate Market Structure Intelligence
        # ==========================================

        structure_result = (
            MarketStructureAgent.analyze(
                price_structure=(
                    price_structure
                ),
                liquidity_sweep=(
                    has_liquidity_sweep
                ),
                order_block=(
                    order_block_direction
                ),
                fair_value_gap=(
                    has_fvg
                ),
                bos=bos,
                choch=choch,
                liquidity_sweep_details=(
                    liquidity_sweep
                ),
                order_block_details=(
                    order_block
                ),
                fvg_details=fvg,
                swing_highs=(
                    swing_highs
                ),
                swing_lows=(
                    swing_lows
                ),
            )
        )

        return structure_result

    # ======================================================
    # CLEANUP
    # ======================================================

    def close(self):
        """
        Close the MetaTrader 5 connection.
        """

        self.provider.disconnect()