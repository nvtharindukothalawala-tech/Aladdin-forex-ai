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

    @staticmethod
    def detect_support_resistance_zones(
        swing_highs,
        swing_lows,
        tolerance,
        min_touches=2,
    ):
        """
        Detect support and resistance zones from
        confirmed swing points.

        Support zones are created from clustered
        swing lows.

        Resistance zones are created from clustered
        swing highs.

        A swing belongs to an existing cluster when
        its price is within tolerance of the current
        cluster center.

        Only clusters containing at least
        min_touches are returned.
        """

        if tolerance < 0:
            raise ValueError("Tolerance cannot be negative.")

        if min_touches < 1:
            raise ValueError("min_touches must be at least 1.")

        def build_zones(
            swing_points,
            zone_type,
        ):
            """
            Cluster swing points chronologically
            and convert confirmed clusters to zones.
            """

            if not swing_points:
                return []

            points = sorted(
                swing_points,
                key=lambda item: item["index"],
            )

            clusters = []

            for point in points:

                price = point["price"]

                matched_cluster = None

                for cluster in clusters:

                    center_price = (
                        sum(
                            item["price"]
                            for item in cluster
                        )
                        / len(cluster)
                    )

                    if abs(price - center_price) <= tolerance:
                        matched_cluster = cluster
                        break

                if matched_cluster is None:
                    clusters.append([point])
                else:
                    matched_cluster.append(point)

            zones = []

            for cluster in clusters:

                if len(cluster) < min_touches:
                    continue

                prices = [
                    item["price"]
                    for item in cluster
                ]

                indices = [
                    item["index"]
                    for item in cluster
                ]

                zones.append(
                    {
                        "type": zone_type,
                        "lower_price": min(prices),
                        "upper_price": max(prices),
                        "center_price": round(
                            sum(prices) / len(prices),
                            6,
                        ),
                        "touch_count": len(cluster),
                        "first_index": min(indices),
                        "last_index": max(indices),
                    }
                )

            return zones

        support_zones = build_zones(
            swing_lows,
            "SUPPORT",
        )

        resistance_zones = build_zones(
            swing_highs,
            "RESISTANCE",
        )

        return {
            "support_zones": support_zones,
            "resistance_zones": resistance_zones,
        }

    @staticmethod
    def detect_engulfing(candles):
        """
        Detect the latest confirmed bullish or bearish
        engulfing candle pattern.

        Bullish engulfing:
        - previous candle is bearish
        - current candle is bullish
        - current real body engulfs previous real body

        Bearish engulfing:
        - previous candle is bullish
        - current candle is bearish
        - current real body engulfs previous real body

        Returns:
            dict | None
        """

        if len(candles) < 2:
            return None

        latest_engulfing = None

        for index in range(
            1,
            len(candles),
        ):
            previous = candles[index - 1]
            current = candles[index]

            previous_bullish = (
                previous.close_price
                > previous.open_price
            )

            previous_bearish = (
                previous.close_price
                < previous.open_price
            )

            current_bullish = (
                current.close_price
                > current.open_price
            )

            current_bearish = (
                current.close_price
                < current.open_price
            )

            # ------------------------------------------
            # Bullish engulfing
            # ------------------------------------------

            if (
                previous_bearish
                and current_bullish
                and current.open_price
                <= previous.close_price
                and current.close_price
                >= previous.open_price
            ):
                latest_engulfing = {
                    "type": "ENGULFING_BULLISH",
                    "previous_index": index - 1,
                    "engulfing_index": index,
                    "open_price": current.open_price,
                    "close_price": current.close_price,
                    "high_price": current.high_price,
                    "low_price": current.low_price,
                    "timestamp": current.timestamp,
                }

            # ------------------------------------------
            # Bearish engulfing
            # ------------------------------------------

            elif (
                previous_bullish
                and current_bearish
                and current.open_price
                >= previous.close_price
                and current.close_price
                <= previous.open_price
            ):
                latest_engulfing = {
                    "type": "ENGULFING_BEARISH",
                    "previous_index": index - 1,
                    "engulfing_index": index,
                    "open_price": current.open_price,
                    "close_price": current.close_price,
                    "high_price": current.high_price,
                    "low_price": current.low_price,
                    "timestamp": current.timestamp,
                }

        return latest_engulfing

    @staticmethod
    def detect_displacement(
        candles,
        atr,
        body_multiplier=1.5,
    ):
        """
        Detect the latest strong displacement candle.

        A displacement candle must have a real body
        significantly larger than current ATR.

        Args:
            candles:
                Candle sequence.

            atr:
                Current Average True Range.

            body_multiplier:
                Required candle-body / ATR ratio.

        Returns:
            dict | None
        """

        if not candles:
            return None

        if atr is None or atr <= 0:
            return None

        latest_displacement = None

        for index, candle in enumerate(candles):

            body_size = abs(
                candle.close_price
                - candle.open_price
            )

            body_atr_ratio = (
                body_size / atr
            )

            if body_atr_ratio < body_multiplier:
                continue

            if (
                candle.close_price
                > candle.open_price
            ):
                displacement_type = (
                    "DISPLACEMENT_BULLISH"
                )

            elif (
                candle.close_price
                < candle.open_price
            ):
                displacement_type = (
                    "DISPLACEMENT_BEARISH"
                )

            else:
                continue

            latest_displacement = {
                "type": displacement_type,
                "candle_index": index,
                "open_price": candle.open_price,
                "close_price": candle.close_price,
                "high_price": candle.high_price,
                "low_price": candle.low_price,
                "body_size": round(
                    body_size,
                    6,
                ),
                "body_atr_ratio": round(
                    body_atr_ratio,
                    3,
                ),
                "timestamp": candle.timestamp,
            }

        return latest_displacement

    def close(self):
        """
        Close the MetaTrader 5 connection.
        """

        self.provider.disconnect()

    # ==========================================================
    # PREMIUM / DISCOUNT / EQUILIBRIUM
    # ==========================================================

    @staticmethod
    def detect_premium_discount(
        swing_highs: list[dict],
        swing_lows: list[dict],
    ) -> dict | None:
        """
        Build the current premium / discount dealing range
        from the latest confirmed swing high and swing low.

        This method is visualization / market-structure logic
        only. It does not execute trades or modify orders.

        The latest swing high and latest swing low are selected
        by their candle index rather than relying on input-list
        ordering.

        The resulting range is divided into:

        - discount: range low -> equilibrium
        - equilibrium: 50% of the dealing range
        - premium: equilibrium -> range high

        Returns None when a valid dealing range cannot be
        constructed.
        """

        # --------------------------------------------------
        # Both sides of the dealing range are required.
        # --------------------------------------------------

        if not swing_highs or not swing_lows:
            return None

        # --------------------------------------------------
        # Select the latest confirmed swing on each side.
        #
        # Do not assume the input arrays are chronological.
        # Using the index makes the result deterministic.
        # --------------------------------------------------

        try:
            latest_high = max(
                swing_highs,
                key=lambda point: int(
                    point["index"]
                ),
            )

            latest_low = max(
                swing_lows,
                key=lambda point: int(
                    point["index"]
                ),
            )

            high_price = float(
                latest_high["price"]
            )

            low_price = float(
                latest_low["price"]
            )

            high_index = int(
                latest_high["index"]
            )

            low_index = int(
                latest_low["index"]
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            return None

        # --------------------------------------------------
        # The prices determine the actual upper and lower
        # boundaries. This supports both:
        #
        # low -> high bullish ranges
        # high -> low bearish ranges
        # --------------------------------------------------

        range_high = max(
            high_price,
            low_price,
        )

        range_low = min(
            high_price,
            low_price,
        )

        # --------------------------------------------------
        # Reject a zero-width or otherwise invalid range.
        # --------------------------------------------------

        if range_high <= range_low:
            return None

        # --------------------------------------------------
        # 50% equilibrium.
        # --------------------------------------------------

        equilibrium = (
            range_low
            + (
                range_high
                - range_low
            )
            / 2
        )

        # --------------------------------------------------
        # Return a stable visualization contract.
        # --------------------------------------------------

        return {
            "range_low": range_low,
            "range_high": range_high,
            "equilibrium": equilibrium,
            "discount_low": range_low,
            "discount_high": equilibrium,
            "premium_low": equilibrium,
            "premium_high": range_high,
            "low_index": low_index,
            "high_index": high_index,
        }