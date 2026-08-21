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

    def close(self):
        """
        Close the MetaTrader 5 connection.
        """

        self.provider.disconnect()