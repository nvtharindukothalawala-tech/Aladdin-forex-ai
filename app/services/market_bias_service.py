"""
market_bias_service.py

Deterministic market-bias scoring for the
Aladdin Forex AI trading terminal.

The service combines already-calculated technical
indicators and confirmed market-structure events.

It does NOT:
- fetch MT5 data
- execute trades
- modify orders
- make broker requests

Author: Tharindu Kothalawala
Project: Aladdin
"""


class MarketBiasService:
    """
    Convert technical and market-structure evidence
    into a deterministic directional market bias.

    Output directions:

        BULLISH
        BEARISH
        NEUTRAL
    """

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"

    # ----------------------------------------------------------
    # Score weights
    # ----------------------------------------------------------

    EMA_WEIGHT = 2.0
    RSI_WEIGHT = 1.0
    ADX_TREND_BONUS = 0.5

    BOS_WEIGHT = 3.0
    CHOCH_WEIGHT = 3.0

    LIQUIDITY_WEIGHT = 1.5
    ORDER_BLOCK_WEIGHT = 1.0
    FVG_WEIGHT = 1.0
    ENGULFING_WEIGHT = 1.0
    DISPLACEMENT_WEIGHT = 1.5

    PREMIUM_DISCOUNT_WEIGHT = 0.5

    # Minimum absolute score required before
    # directional bias is returned.
    DIRECTION_THRESHOLD = 2.0

    # ADX threshold commonly used here to distinguish
    # weak directional conditions from stronger trend.
    ADX_TREND_THRESHOLD = 20.0

    # RSI directional center.
    RSI_MIDPOINT = 50.0

    @staticmethod
    def _latest_indicator_value(
        series,
    ):
        """
        Return the latest numeric value from an indicator
        series.

        Supports either:

            [{"time": ..., "value": 1.23}]

        or:

            [1.1, 1.2, 1.3]

        Returns None when a valid value cannot be found.
        """

        if not series:
            return None

        latest = series[-1]

        if isinstance(latest, dict):
            value = latest.get("value")
        else:
            value = latest

        if value is None:
            return None

        try:
            return float(value)

        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _event_type(
        event,
    ):
        """
        Safely extract an event type.
        """

        if not event:
            return None

        if not isinstance(event, dict):
            return None

        event_type = event.get("type")

        if not isinstance(event_type, str):
            return None

        return event_type.upper()

    @staticmethod
    def _add_reason(
        reasons,
        source,
        direction,
        weight,
        message,
    ):
        """
        Add one evidence item to the explanation list.
        """

        reasons.append(
            {
                "source": source,
                "direction": direction,
                "weight": weight,
                "message": message,
            }
        )

    @classmethod
    def analyze(
        cls,
        *,
        candles,
        ema20_series,
        rsi14_series,
        adx14_series,
        latest_bos=None,
        latest_choch=None,
        latest_liquidity_sweep=None,
        latest_order_block=None,
        latest_fvg=None,
        latest_engulfing=None,
        latest_displacement=None,
        latest_premium_discount=None,
    ):
        """
        Calculate deterministic market bias.

        All inputs must already have been calculated by
        the caller from the same candle dataset.

        Returns:

            {
                "bias": "BULLISH",
                "score": 5.5,
                "confidence": 68.75,
                "bullish_score": 7.0,
                "bearish_score": 1.5,
                "reasons": [...]
            }
        """

        if not candles:
            raise ValueError(
                "Market bias requires candle data."
            )

        latest_candle = candles[-1]

        try:
            current_close = float(
                latest_candle.close_price
            )

        except (
            AttributeError,
            TypeError,
            ValueError,
        ) as error:

            raise ValueError(
                "Latest candle does not contain "
                "a valid close price."
            ) from error

        ema20 = cls._latest_indicator_value(
            ema20_series
        )

        rsi14 = cls._latest_indicator_value(
            rsi14_series
        )

        adx14 = cls._latest_indicator_value(
            adx14_series
        )

        bullish_score = 0.0
        bearish_score = 0.0

        reasons = []

        # ======================================================
        # EMA 20
        # ======================================================

        if ema20 is not None:

            if current_close > ema20:

                bullish_score += cls.EMA_WEIGHT

                cls._add_reason(
                    reasons,
                    "EMA20",
                    cls.BULLISH,
                    cls.EMA_WEIGHT,
                    "Price is above EMA 20.",
                )

            elif current_close < ema20:

                bearish_score += cls.EMA_WEIGHT

                cls._add_reason(
                    reasons,
                    "EMA20",
                    cls.BEARISH,
                    cls.EMA_WEIGHT,
                    "Price is below EMA 20.",
                )

        # ======================================================
        # RSI 14
        # ======================================================

        if rsi14 is not None:

            if rsi14 > cls.RSI_MIDPOINT:

                bullish_score += cls.RSI_WEIGHT

                cls._add_reason(
                    reasons,
                    "RSI14",
                    cls.BULLISH,
                    cls.RSI_WEIGHT,
                    "RSI 14 is above 50.",
                )

            elif rsi14 < cls.RSI_MIDPOINT:

                bearish_score += cls.RSI_WEIGHT

                cls._add_reason(
                    reasons,
                    "RSI14",
                    cls.BEARISH,
                    cls.RSI_WEIGHT,
                    "RSI 14 is below 50.",
                )

        # ======================================================
        # ADX 14
        #
        # ADX itself is non-directional.
        #
        # It only strengthens the side already supported by
        # price vs EMA.
        # ======================================================

        if (
            adx14 is not None
            and adx14 >= cls.ADX_TREND_THRESHOLD
            and ema20 is not None
        ):

            if current_close > ema20:

                bullish_score += (
                    cls.ADX_TREND_BONUS
                )

                cls._add_reason(
                    reasons,
                    "ADX14",
                    cls.BULLISH,
                    cls.ADX_TREND_BONUS,
                    "ADX confirms stronger bullish "
                    "trend conditions.",
                )

            elif current_close < ema20:

                bearish_score += (
                    cls.ADX_TREND_BONUS
                )

                cls._add_reason(
                    reasons,
                    "ADX14",
                    cls.BEARISH,
                    cls.ADX_TREND_BONUS,
                    "ADX confirms stronger bearish "
                    "trend conditions.",
                )

        # ======================================================
        # BOS
        # ======================================================

        bos_type = cls._event_type(
            latest_bos
        )

        if bos_type == "BOS_BULLISH":

            bullish_score += cls.BOS_WEIGHT

            cls._add_reason(
                reasons,
                "BOS",
                cls.BULLISH,
                cls.BOS_WEIGHT,
                "Latest break of structure is bullish.",
            )

        elif bos_type == "BOS_BEARISH":

            bearish_score += cls.BOS_WEIGHT

            cls._add_reason(
                reasons,
                "BOS",
                cls.BEARISH,
                cls.BOS_WEIGHT,
                "Latest break of structure is bearish.",
            )

        # ======================================================
        # CHoCH
        # ======================================================

        choch_type = cls._event_type(
            latest_choch
        )

        if choch_type == "CHOCH_BULLISH":

            bullish_score += cls.CHOCH_WEIGHT

            cls._add_reason(
                reasons,
                "CHoCH",
                cls.BULLISH,
                cls.CHOCH_WEIGHT,
                "Latest change of character is bullish.",
            )

        elif choch_type == "CHOCH_BEARISH":

            bearish_score += cls.CHOCH_WEIGHT

            cls._add_reason(
                reasons,
                "CHoCH",
                cls.BEARISH,
                cls.CHOCH_WEIGHT,
                "Latest change of character is bearish.",
            )

        # ======================================================
        # LIQUIDITY SWEEP
        #
        # High-side sweep -> bearish rejection evidence.
        # Low-side sweep  -> bullish rejection evidence.
        # ======================================================

        liquidity_type = cls._event_type(
            latest_liquidity_sweep
        )

        if (
            liquidity_type
            == "LIQUIDITY_SWEEP_LOW"
        ):

            bullish_score += (
                cls.LIQUIDITY_WEIGHT
            )

            cls._add_reason(
                reasons,
                "LIQUIDITY",
                cls.BULLISH,
                cls.LIQUIDITY_WEIGHT,
                "Low-side liquidity was swept and "
                "price closed back above the level.",
            )

        elif (
            liquidity_type
            == "LIQUIDITY_SWEEP_HIGH"
        ):

            bearish_score += (
                cls.LIQUIDITY_WEIGHT
            )

            cls._add_reason(
                reasons,
                "LIQUIDITY",
                cls.BEARISH,
                cls.LIQUIDITY_WEIGHT,
                "High-side liquidity was swept and "
                "price closed back below the level.",
            )

        # ======================================================
        # ORDER BLOCK
        # ======================================================

        order_block_type = cls._event_type(
            latest_order_block
        )

        if (
            order_block_type
            == "ORDER_BLOCK_BULLISH"
        ):

            bullish_score += (
                cls.ORDER_BLOCK_WEIGHT
            )

            cls._add_reason(
                reasons,
                "ORDER_BLOCK",
                cls.BULLISH,
                cls.ORDER_BLOCK_WEIGHT,
                "Latest detected order block is bullish.",
            )

        elif (
            order_block_type
            == "ORDER_BLOCK_BEARISH"
        ):

            bearish_score += (
                cls.ORDER_BLOCK_WEIGHT
            )

            cls._add_reason(
                reasons,
                "ORDER_BLOCK",
                cls.BEARISH,
                cls.ORDER_BLOCK_WEIGHT,
                "Latest detected order block is bearish.",
            )

        # ======================================================
        # FAIR VALUE GAP
        # ======================================================

        fvg_type = cls._event_type(
            latest_fvg
        )

        if fvg_type == "FVG_BULLISH":

            bullish_score += cls.FVG_WEIGHT

            cls._add_reason(
                reasons,
                "FVG",
                cls.BULLISH,
                cls.FVG_WEIGHT,
                "Latest fair value gap is bullish.",
            )

        elif fvg_type == "FVG_BEARISH":

            bearish_score += cls.FVG_WEIGHT

            cls._add_reason(
                reasons,
                "FVG",
                cls.BEARISH,
                cls.FVG_WEIGHT,
                "Latest fair value gap is bearish.",
            )

        # ======================================================
        # ENGULFING
        # ======================================================

        engulfing_type = cls._event_type(
            latest_engulfing
        )

        if (
            engulfing_type
            == "ENGULFING_BULLISH"
        ):

            bullish_score += (
                cls.ENGULFING_WEIGHT
            )

            cls._add_reason(
                reasons,
                "ENGULFING",
                cls.BULLISH,
                cls.ENGULFING_WEIGHT,
                "Latest engulfing pattern is bullish.",
            )

        elif (
            engulfing_type
            == "ENGULFING_BEARISH"
        ):

            bearish_score += (
                cls.ENGULFING_WEIGHT
            )

            cls._add_reason(
                reasons,
                "ENGULFING",
                cls.BEARISH,
                cls.ENGULFING_WEIGHT,
                "Latest engulfing pattern is bearish.",
            )

        # ======================================================
        # DISPLACEMENT
        # ======================================================

        displacement_type = cls._event_type(
            latest_displacement
        )

        if (
            displacement_type
            == "DISPLACEMENT_BULLISH"
        ):

            bullish_score += (
                cls.DISPLACEMENT_WEIGHT
            )

            cls._add_reason(
                reasons,
                "DISPLACEMENT",
                cls.BULLISH,
                cls.DISPLACEMENT_WEIGHT,
                "Latest strong displacement is bullish.",
            )

        elif (
            displacement_type
            == "DISPLACEMENT_BEARISH"
        ):

            bearish_score += (
                cls.DISPLACEMENT_WEIGHT
            )

            cls._add_reason(
                reasons,
                "DISPLACEMENT",
                cls.BEARISH,
                cls.DISPLACEMENT_WEIGHT,
                "Latest strong displacement is bearish.",
            )

        # ======================================================
        # PREMIUM / DISCOUNT
        #
        # This is intentionally low weight because location
        # alone should not determine market direction.
        # ======================================================

        if latest_premium_discount:

            try:

                equilibrium = float(
                    latest_premium_discount[
                        "equilibrium"
                    ]
                )

                range_low = float(
                    latest_premium_discount[
                        "range_low"
                    ]
                )

                range_high = float(
                    latest_premium_discount[
                        "range_high"
                    ]
                )

                if (
                    range_low
                    <= current_close
                    < equilibrium
                ):

                    bullish_score += (
                        cls.PREMIUM_DISCOUNT_WEIGHT
                    )

                    cls._add_reason(
                        reasons,
                        "PREMIUM_DISCOUNT",
                        cls.BULLISH,
                        cls.PREMIUM_DISCOUNT_WEIGHT,
                        "Price is trading in the "
                        "discount half of the current "
                        "dealing range.",
                    )

                elif (
                    equilibrium
                    < current_close
                    <= range_high
                ):

                    bearish_score += (
                        cls.PREMIUM_DISCOUNT_WEIGHT
                    )

                    cls._add_reason(
                        reasons,
                        "PREMIUM_DISCOUNT",
                        cls.BEARISH,
                        cls.PREMIUM_DISCOUNT_WEIGHT,
                        "Price is trading in the "
                        "premium half of the current "
                        "dealing range.",
                    )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                pass

        # ======================================================
        # FINAL SCORE
        # ======================================================

        bullish_score = round(
            bullish_score,
            2,
        )

        bearish_score = round(
            bearish_score,
            2,
        )

        net_score = round(
            bullish_score - bearish_score,
            2,
        )

        # ======================================================
        # BIAS
        # ======================================================

        if net_score >= cls.DIRECTION_THRESHOLD:

            bias = cls.BULLISH

        elif net_score <= -cls.DIRECTION_THRESHOLD:

            bias = cls.BEARISH

        else:

            bias = cls.NEUTRAL

        # ======================================================
        # CONFIDENCE
        #
        # Confidence describes evidence dominance.
        #
        # Example:
        #
        # bullish = 8
        # bearish = 2
        #
        # dominance = 6 / 10 = 60%
        #
        # This avoids pretending that a raw score itself
        # is a probability of future price movement.
        # ======================================================

        total_directional_evidence = (
            bullish_score
            + bearish_score
        )

        if total_directional_evidence > 0:

            confidence = (
                abs(net_score)
                / total_directional_evidence
                * 100
            )

        else:

            confidence = 0.0

        confidence = round(
            min(
                confidence,
                100.0,
            ),
            2,
        )

        # ======================================================
        # RETURN CONTRACT
        # ======================================================

        return {
            "bias": bias,
            "score": net_score,
            "confidence": confidence,
            "bullish_score": bullish_score,
            "bearish_score": bearish_score,
            "current_close": current_close,
            "ema20": ema20,
            "rsi14": rsi14,
            "adx14": adx14,
            "reasons": reasons,
        }