"""
market_structure_service.py

Detects market structure from real
MetaTrader 5 candle data.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from app.market.mt5_provider import MT5DataProvider


class MarketStructureService:
    """
    Detect market structure using Forex candles.
    """

    def __init__(self):
        """
        Create the market structure service.
        """

        self.provider = MT5DataProvider()

    @staticmethod
    def find_swing_highs(
        candles,
        lookback=2,
    ):
        """
        Find swing high candles.

        A candle is considered a swing high
        when its high is higher than the highs
        of nearby candles.
        """

        swing_highs = []

        for index in range(
            lookback,
            len(candles) - lookback,
        ):

            current = candles[index]

            is_swing_high = True

            for offset in range(
                1,
                lookback + 1,
            ):

                left = candles[index - offset]
                right = candles[index + offset]

                if (
                    current.high_price <= left.high_price
                    or current.high_price <= right.high_price
                ):
                    is_swing_high = False

                    break

            if is_swing_high:

                swing_highs.append(
                    {
                        "index": index,
                        "price": current.high_price,
                        "timestamp": current.timestamp,
                    }
                )

        return swing_highs

    @staticmethod
    def find_swing_lows(
        candles,
        lookback=2,
    ):
        """
        Find swing low candles.

        A candle is considered a swing low
        when its low is lower than the lows
        of nearby candles.
        """

        swing_lows = []

        for index in range(
            lookback,
            len(candles) - lookback,
        ):

            current = candles[index]

            is_swing_low = True

            for offset in range(
                1,
                lookback + 1,
            ):

                left = candles[index - offset]
                right = candles[index + offset]

                if (
                    current.low_price >= left.low_price
                    or current.low_price >= right.low_price
                ):
                    is_swing_low = False

                    break

            if is_swing_low:

                swing_lows.append(
                    {
                        "index": index,
                        "price": current.low_price,
                        "timestamp": current.timestamp,
                    }
                )

        return swing_lows

    def get_structure_points(
        self,
        symbol,
        timeframe,
        candle_count=1000,
        lookback=2,
    ):
        """
        Get swing highs and swing lows
        from real MT5 market data.
        """

        candles = self.provider.get_candles(
            symbol=symbol,
            timeframe=timeframe,
            count=candle_count,
        )

        if not candles:
            raise ValueError(
                f"No market data available for {symbol}."
            )

        swing_highs = self.find_swing_highs(
            candles,
            lookback=lookback,
        )

        swing_lows = self.find_swing_lows(
            candles,
            lookback=lookback,
        )

        return {
            "symbol": symbol,
            "timeframe": str(timeframe),
            "candle_count": len(candles),
            "swing_highs": swing_highs,
            "swing_lows": swing_lows,
        }

    @staticmethod
    def detect_bos(
        candles,
        swing_highs,
        swing_lows,
    ):
        """
        Detect the latest Break of Structure (BOS).

        Bullish BOS:
            Price closes above a confirmed swing high.

        Bearish BOS:
            Price closes below a confirmed swing low.
        """

        bullish_breaks = []

        bearish_breaks = []

        # ==========================================
        # Bullish BOS
        # ==========================================

        for swing_high in swing_highs:

            swing_index = swing_high["index"]
            swing_price = swing_high["price"]

            for index in range(
                swing_index + 1,
                len(candles),
            ):

                candle = candles[index]

                if candle.close_price > swing_price:

                    bullish_breaks.append(
                        {
                            "type": "BOS_BULLISH",
                            "broken_price": swing_price,
                            "swing_index": swing_index,
                            "break_index": index,
                            "timestamp": candle.timestamp,
                        }
                    )

                    break

        # ==========================================
        # Bearish BOS
        # ==========================================

        for swing_low in swing_lows:

            swing_index = swing_low["index"]
            swing_price = swing_low["price"]

            for index in range(
                swing_index + 1,
                len(candles),
            ):

                candle = candles[index]

                if candle.close_price < swing_price:

                    bearish_breaks.append(
                        {
                            "type": "BOS_BEARISH",
                            "broken_price": swing_price,
                            "swing_index": swing_index,
                            "break_index": index,
                            "timestamp": candle.timestamp,
                        }
                    )

                    break

        # ==========================================
        # Find latest BOS
        # ==========================================

        all_breaks = (
            bullish_breaks
            + bearish_breaks
        )

        if not all_breaks:

            return None

        latest_break = max(
            all_breaks,
            key=lambda item: item["break_index"],
        )

        return latest_break

    @staticmethod
    def detect_choch(
        candles,
        swing_highs,
        swing_lows,
        latest_bos,
    ):
        """
        Detect the latest Change of Character (CHoCH).

        After a bullish BOS:
            A close below a later swing low
            can indicate bearish CHoCH.

        After a bearish BOS:
            A close above a later swing high
            can indicate bullish CHoCH.
        """

        if latest_bos is None:
            return None

        choch_events = []

        bos_type = latest_bos["type"]
        bos_break_index = latest_bos["break_index"]

        # ==========================================
        # Bullish structure -> Bearish CHoCH
        # ==========================================

        if bos_type == "BOS_BULLISH":

            for swing_low in swing_lows:

                swing_index = swing_low["index"]
                swing_price = swing_low["price"]

                # Only use swing lows formed after BOS
                if swing_index <= bos_break_index:
                    continue

                for index in range(
                    swing_index + 1,
                    len(candles),
                ):

                    candle = candles[index]

                    if candle.close_price < swing_price:

                        choch_events.append(
                            {
                                "type": "CHOCH_BEARISH",
                                "broken_price": swing_price,
                                "swing_index": swing_index,
                                "break_index": index,
                                "timestamp": candle.timestamp,
                            }
                        )

                        break

        # ==========================================
        # Bearish structure -> Bullish CHoCH
        # ==========================================

        elif bos_type == "BOS_BEARISH":

            for swing_high in swing_highs:

                swing_index = swing_high["index"]
                swing_price = swing_high["price"]

                # Only use swing highs formed after BOS
                if swing_index <= bos_break_index:
                    continue

                for index in range(
                    swing_index + 1,
                    len(candles),
                ):

                    candle = candles[index]

                    if candle.close_price > swing_price:

                        choch_events.append(
                            {
                                "type": "CHOCH_BULLISH",
                                "broken_price": swing_price,
                                "swing_index": swing_index,
                                "break_index": index,
                                "timestamp": candle.timestamp,
                            }
                        )

                        break

        if not choch_events:
            return None

        return max(
            choch_events,
            key=lambda item: item["break_index"],
        )

    @staticmethod
    def detect_liquidity_sweep(
        candles,
        swing_highs,
        swing_lows,
    ):
        """
        Detect the latest liquidity sweep.

        High-side sweep:
            Candle high moves above a confirmed swing high
            but candle closes back below that level.

        Low-side sweep:
            Candle low moves below a confirmed swing low
            but candle closes back above that level.
        """

        sweep_events = []

        # ==========================================
        # High-side liquidity sweep
        # ==========================================

        for swing_high in swing_highs:

            swing_index = swing_high["index"]
            swing_price = swing_high["price"]

            for index in range(
                swing_index + 1,
                len(candles),
            ):

                candle = candles[index]

                if (
                    candle.high_price > swing_price
                    and candle.close_price < swing_price
                ):

                    sweep_events.append(
                        {
                            "type": "LIQUIDITY_SWEEP_HIGH",
                            "level_price": swing_price,
                            "swing_index": swing_index,
                            "sweep_index": index,
                            "timestamp": candle.timestamp,
                        }
                    )

                    break

        # ==========================================
        # Low-side liquidity sweep
        # ==========================================

        for swing_low in swing_lows:

            swing_index = swing_low["index"]
            swing_price = swing_low["price"]

            for index in range(
                swing_index + 1,
                len(candles),
            ):

                candle = candles[index]

                if (
                    candle.low_price < swing_price
                    and candle.close_price > swing_price
                ):

                    sweep_events.append(
                        {
                            "type": "LIQUIDITY_SWEEP_LOW",
                            "level_price": swing_price,
                            "swing_index": swing_index,
                            "sweep_index": index,
                            "timestamp": candle.timestamp,
                        }
                    )

                    break

        # ==========================================
        # No sweep detected
        # ==========================================

        if not sweep_events:
            return None

        # ==========================================
        # Return latest sweep
        # ==========================================

        return max(
            sweep_events,
            key=lambda item: item["sweep_index"],
        )

    @staticmethod
    def detect_order_block(
        candles,
        latest_bos,
    ):
        """
        Detect the latest Order Block related to BOS.

        Bullish Order Block:
            The last bearish candle before
            a bullish BOS.

        Bearish Order Block:
            The last bullish candle before
            a bearish BOS.
        """

        if latest_bos is None:
            return None

        bos_type = latest_bos["type"]
        break_index = latest_bos["break_index"]

        # We need at least one candle before the BOS.
        if break_index <= 0:
            return None

        # ==========================================
        # Bullish Order Block
        # ==========================================

        if bos_type == "BOS_BULLISH":

            for index in range(
                break_index - 1,
                -1,
                -1,
            ):

                candle = candles[index]

                # Bearish candle
                if candle.close_price < candle.open_price:

                    return {
                        "type": "ORDER_BLOCK_BULLISH",
                        "candle_index": index,
                        "high_price": candle.high_price,
                        "low_price": candle.low_price,
                        "open_price": candle.open_price,
                        "close_price": candle.close_price,
                        "timestamp": candle.timestamp,
                    }

        # ==========================================
        # Bearish Order Block
        # ==========================================

        elif bos_type == "BOS_BEARISH":

            for index in range(
                break_index - 1,
                -1,
                -1,
            ):

                candle = candles[index]

                # Bullish candle
                if candle.close_price > candle.open_price:

                    return {
                        "type": "ORDER_BLOCK_BEARISH",
                        "candle_index": index,
                        "high_price": candle.high_price,
                        "low_price": candle.low_price,
                        "open_price": candle.open_price,
                        "close_price": candle.close_price,
                        "timestamp": candle.timestamp,
                    }

        return None

    @staticmethod
    def detect_fvg(
        candles,
    ):
        """
        Detect the latest Fair Value Gap (FVG).

        Bullish FVG:
            Candle 3 low is above Candle 1 high.

        Bearish FVG:
            Candle 3 high is below Candle 1 low.

        The middle candle is the displacement candle.
        """

        fvg_events = []

        if len(candles) < 3:
            return None

        # ==========================================
        # Scan 3-candle patterns
        # ==========================================

        for index in range(
            2,
            len(candles),
        ):

            candle_1 = candles[index - 2]
            candle_2 = candles[index - 1]
            candle_3 = candles[index]

            # ==========================================
            # Bullish FVG
            # ==========================================

            if candle_3.low_price > candle_1.high_price:

                fvg_events.append(
                    {
                        "type": "FVG_BULLISH",
                        "start_index": index - 2,
                        "middle_index": index - 1,
                        "end_index": index,
                        "lower_price": candle_1.high_price,
                        "upper_price": candle_3.low_price,
                        "timestamp": candle_3.timestamp,
                    }
                )

            # ==========================================
            # Bearish FVG
            # ==========================================

            elif candle_3.high_price < candle_1.low_price:

                fvg_events.append(
                    {
                        "type": "FVG_BEARISH",
                        "start_index": index - 2,
                        "middle_index": index - 1,
                        "end_index": index,
                        "lower_price": candle_3.high_price,
                        "upper_price": candle_1.low_price,
                        "timestamp": candle_3.timestamp,
                    }
                )

        # ==========================================
        # No FVG detected
        # ==========================================

        if not fvg_events:
            return None

        # ==========================================
        # Return latest FVG
        # ==========================================

        return max(
            fvg_events,
            key=lambda item: item["end_index"],
        )

    def close(self):
        """
        Close the MetaTrader 5 connection.
        """

        self.provider.disconnect()