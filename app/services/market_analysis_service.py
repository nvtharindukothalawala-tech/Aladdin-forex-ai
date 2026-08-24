"""
market_analysis_service.py

Connects MetaTrader 5 market data with
Aladdin technical analysis.

Author: Tharindu Kothalawala
Project: Aladdin
"""

import MetaTrader5 as mt5

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
    """

    def __init__(self):
        """
        Create the market analysis service.
        """

        self.provider = MT5DataProvider()

    def analyze(
        self,
        symbol,
        timeframe=mt5.TIMEFRAME_H1,
        candle_count=1000,
    ):
        """
        Get market data and perform technical analysis.

        Args:
            symbol:
                MT5 symbol, for example EURUSD.

            timeframe:
                MT5 timeframe.

            candle_count:
                Number of candles used for analysis.

        Returns:
            MarketSignal containing the analysis.
        """

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

        # Calculate technical indicators

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

        # Latest closing price

        current_price = candles[-1].close_price

        # Generate market signal

        signal = MarketAnalyzer.analyze(
            symbol=symbol,
            current_price=current_price,
            ema=ema,
            rsi=rsi,
            atr=atr,
            adx=adx,
        )

        return signal

    def analyze_structure(
        self,
        symbol,
        timeframe=mt5.TIMEFRAME_H1,
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
        # Convert BOS to structure input
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

            if order_block["type"] == "ORDER_BLOCK_BULLISH":

                order_block_direction = "BULLISH"

            elif order_block["type"] == "ORDER_BLOCK_BEARISH":

                order_block_direction = "BEARISH"

            else:

                order_block_direction = "NONE"

        else:

            order_block_direction = "NONE"

        # ==========================================
        # FVG Detection
        # ==========================================

        has_fvg = fvg is not None

        # ==========================================
        # Generate Market Structure Intelligence
        # ==========================================

        structure_result = MarketStructureAgent.analyze(
            price_structure=price_structure,
            liquidity_sweep=has_liquidity_sweep,
            order_block=order_block_direction,
            fair_value_gap=has_fvg,
            bos=bos,
            choch=choch,
            liquidity_sweep_details=liquidity_sweep,
            order_block_details=order_block,
            fvg_details=fvg,
            swing_highs=swing_highs,
            swing_lows=swing_lows,
        )

        # ==========================================
        # Return Structure Result
        # ==========================================

        return structure_result

    def close(self):
        """
        Close the MetaTrader 5 connection.
        """

        self.provider.disconnect()