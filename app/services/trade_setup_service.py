"""
trade_setup_service.py

Deterministic trade-setup generation for Aladdin.

This service converts already-calculated market analysis into an
explainable TRADE or WAIT decision.

IMPORTANT:
- This service does not fetch market data.
- This service does not place, modify, or close trades.
- Market bias alone never creates a trade.
- A valid setup requires directional alignment, a sensible entry
  location, stop-loss placement, and acceptable risk/reward.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from __future__ import annotations

from typing import Any


class TradeSetupService:
    """
    Build deterministic, explainable trade setups from existing
    Aladdin market-analysis results.
    """

    MIN_RISK_REWARD = 1.5

    ENTRY_ATR_TOLERANCE = 0.50
    STOP_ATR_BUFFER = 0.25

    DEFAULT_TARGET_R_MULTIPLES = (
        1.0,
        2.0,
    )

    VALID_BIASES = {
        "BULLISH",
        "BEARISH",
        "NEUTRAL",
    }

    VALID_STRENGTHS = {
        "VERY_WEAK",
        "WEAK",
        "MODERATE",
        "STRONG",
        "VERY_STRONG",
    }

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    @classmethod
    def analyze(
        cls,
        *,
        candles,
        market_bias: dict | None,
        atr: float | None,
        latest_bos: dict | None = None,
        latest_choch: dict | None = None,
        latest_liquidity_sweep: dict | None = None,
        latest_order_block: dict | None = None,
        latest_fvg: dict | None = None,
        latest_premium_discount: dict | None = None,
        support_resistance: dict | None = None,
        symbol: str | None = None,
        timeframe: str | None = None,
    ) -> dict:
        """
        Analyze current market evidence and return either:

            status = TRADE

        or:

            status = WAIT

        No broker action is performed.
        """

        if not candles:
            raise ValueError(
                "Trade setup analysis requires candle data."
            )

        current_price = cls._get_close_price(
            candles[-1]
        )

        if current_price is None:
            raise ValueError(
                "Latest candle does not contain a valid close price."
            )

        normalized_atr = cls._positive_float(
            atr
        )

        if normalized_atr is None:
            return cls._wait_result(
                symbol=symbol,
                timeframe=timeframe,
                current_price=current_price,
                market_bias=market_bias,
                reasons=[
                    "ATR is unavailable or invalid.",
                    "A safe entry and stop-loss distance cannot be calculated.",
                ],
            )

        bias = cls._normalize_bias(
            market_bias
        )

        strength = cls._normalize_strength(
            market_bias
        )

        confidence = cls._market_bias_number(
            market_bias,
            "confidence",
        )

        bias_score = cls._market_bias_number(
            market_bias,
            "score",
        )

        # ------------------------------------------------------
        # Bias is directional context, not a trade signal.
        # ------------------------------------------------------

        if bias == "NEUTRAL":
            return cls._wait_result(
                symbol=symbol,
                timeframe=timeframe,
                current_price=current_price,
                market_bias=market_bias,
                reasons=[
                    "Market bias is neutral.",
                    "No directional trade setup is allowed without directional bias.",
                ],
            )

        if bias not in {
            "BULLISH",
            "BEARISH",
        }:
            return cls._wait_result(
                symbol=symbol,
                timeframe=timeframe,
                current_price=current_price,
                market_bias=market_bias,
                reasons=[
                    "Directional market bias is unavailable.",
                ],
            )

        direction = (
            "BUY"
            if bias == "BULLISH"
            else "SELL"
        )

        reasons: list[str] = []

        reasons.append(
            (
                "Bullish market bias."
                if direction == "BUY"
                else "Bearish market bias."
            )
        )

        if strength:
            reasons.append(
                "Market bias strength is "
                f"{strength.replace('_', ' ').lower()}."
            )

        # ------------------------------------------------------
        # Structural conflict check
        # ------------------------------------------------------

        conflict_reason = (
            cls._find_structure_conflict(
                direction=direction,
                latest_bos=latest_bos,
                latest_choch=latest_choch,
            )
        )

        if conflict_reason is not None:
            return cls._wait_result(
                symbol=symbol,
                timeframe=timeframe,
                current_price=current_price,
                market_bias=market_bias,
                direction=direction,
                reasons=(
                    reasons
                    + [conflict_reason]
                ),
            )

        # ------------------------------------------------------
        # Directional confirmations
        # ------------------------------------------------------

        confirmation_reasons = (
            cls._collect_directional_confirmations(
                direction=direction,
                latest_bos=latest_bos,
                latest_choch=latest_choch,
                latest_liquidity_sweep=(
                    latest_liquidity_sweep
                ),
            )
        )

        reasons.extend(
            confirmation_reasons
        )

        # ------------------------------------------------------
        # Build candidate entry zones.
        # ------------------------------------------------------

        candidate_zones = (
            cls._build_entry_candidates(
                direction=direction,
                current_price=current_price,
                atr=normalized_atr,
                latest_order_block=(
                    latest_order_block
                ),
                latest_fvg=latest_fvg,
                latest_premium_discount=(
                    latest_premium_discount
                ),
                support_resistance=(
                    support_resistance
                ),
            )
        )

        if not candidate_zones:
            return cls._wait_result(
                symbol=symbol,
                timeframe=timeframe,
                current_price=current_price,
                market_bias=market_bias,
                direction=direction,
                reasons=(
                    reasons
                    + [
                        "No valid directional entry zone is available."
                    ]
                ),
            )

        # ------------------------------------------------------
        # Select best candidate by distance from current price.
        # ------------------------------------------------------

        entry_candidate = (
            cls._select_best_entry_candidate(
                candidate_zones,
                current_price=current_price,
            )
        )

        if entry_candidate is None:
            return cls._wait_result(
                symbol=symbol,
                timeframe=timeframe,
                current_price=current_price,
                market_bias=market_bias,
                direction=direction,
                reasons=(
                    reasons
                    + [
                        "No usable entry candidate could be selected."
                    ]
                ),
            )

        entry_low = entry_candidate[
            "low"
        ]

        entry_high = entry_candidate[
            "high"
        ]

        preferred_entry = entry_candidate[
            "preferred"
        ]

        entry_source = entry_candidate[
            "source"
        ]

        # ------------------------------------------------------
        # Reject setups when price is too far from the zone.
        # ------------------------------------------------------

        distance_to_zone = (
            cls._distance_to_zone(
                current_price,
                entry_low,
                entry_high,
            )
        )

        max_entry_distance = (
            normalized_atr
            * cls.ENTRY_ATR_TOLERANCE
        )

        if distance_to_zone > max_entry_distance:
            return cls._wait_result(
                symbol=symbol,
                timeframe=timeframe,
                current_price=current_price,
                market_bias=market_bias,
                direction=direction,
                entry={
                    "type": "ZONE",
                    "source": entry_source,
                    "low": cls._round_price(
                        entry_low
                    ),
                    "high": cls._round_price(
                        entry_high
                    ),
                    "preferred": cls._round_price(
                        preferred_entry
                    ),
                },
                reasons=(
                    reasons
                    + [
                        (
                            f"Valid {entry_source.lower()} "
                            "entry zone exists."
                        ),
                        (
                            "Current price is too far from "
                            "the preferred entry zone."
                        ),
                        "Wait for price to retrace into the entry area.",
                    ]
                ),
            )

        reasons.append(
            f"Price is near a valid {entry_source.lower()} entry zone."
        )

        # ------------------------------------------------------
        # Stop loss
        # ------------------------------------------------------

        stop_loss = cls._calculate_stop_loss(
            direction=direction,
            entry_low=entry_low,
            entry_high=entry_high,
            atr=normalized_atr,
            latest_order_block=(
                latest_order_block
            ),
            latest_liquidity_sweep=(
                latest_liquidity_sweep
            ),
        )

        if stop_loss is None:
            return cls._wait_result(
                symbol=symbol,
                timeframe=timeframe,
                current_price=current_price,
                market_bias=market_bias,
                direction=direction,
                reasons=(
                    reasons
                    + [
                        "A valid stop-loss level could not be calculated."
                    ]
                ),
            )

        risk_distance = (
            preferred_entry - stop_loss
            if direction == "BUY"
            else stop_loss - preferred_entry
        )

        if risk_distance <= 0:
            return cls._wait_result(
                symbol=symbol,
                timeframe=timeframe,
                current_price=current_price,
                market_bias=market_bias,
                direction=direction,
                reasons=(
                    reasons
                    + [
                        "Calculated stop loss is invalid for the trade direction."
                    ]
                ),
            )

        # ------------------------------------------------------
        # Targets
        # ------------------------------------------------------

        targets = cls._build_targets(
            direction=direction,
            entry=preferred_entry,
            risk_distance=risk_distance,
            support_resistance=(
                support_resistance
            ),
        )

        if not targets:
            return cls._wait_result(
                symbol=symbol,
                timeframe=timeframe,
                current_price=current_price,
                market_bias=market_bias,
                direction=direction,
                reasons=(
                    reasons
                    + [
                        "No valid take-profit target could be calculated."
                    ]
                ),
            )

        best_rr = max(
            target["rr"]
            for target in targets
        )

        # ------------------------------------------------------
        # Minimum R:R filter
        # ------------------------------------------------------

        if best_rr < cls.MIN_RISK_REWARD:
            return cls._wait_result(
                symbol=symbol,
                timeframe=timeframe,
                current_price=current_price,
                market_bias=market_bias,
                direction=direction,
                entry={
                    "type": "ZONE",
                    "source": entry_source,
                    "low": cls._round_price(
                        entry_low
                    ),
                    "high": cls._round_price(
                        entry_high
                    ),
                    "preferred": cls._round_price(
                        preferred_entry
                    ),
                },
                stop_loss=cls._round_price(
                    stop_loss
                ),
                targets=targets,
                risk_reward=best_rr,
                reasons=(
                    reasons
                    + [
                        (
                            "Risk/reward requirement is not satisfied."
                        )
                    ]
                ),
            )

        # ------------------------------------------------------
        # Final trade setup
        # ------------------------------------------------------

        reasons.append(
            (
                "Risk/reward requirement is satisfied "
                f"with up to {best_rr:.2f}R."
            )
        )

        invalidation = (
            f"Price closes below {cls._round_price(stop_loss)}."
            if direction == "BUY"
            else
            f"Price closes above {cls._round_price(stop_loss)}."
        )

        return {
            "status": "TRADE",
            "direction": direction,
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": cls._round_price(
                current_price
            ),
            "entry": {
                "type": "ZONE",
                "source": entry_source,
                "low": cls._round_price(
                    entry_low
                ),
                "high": cls._round_price(
                    entry_high
                ),
                "preferred": cls._round_price(
                    preferred_entry
                ),
            },
            "stop_loss": cls._round_price(
                stop_loss
            ),
            "targets": targets,
            "risk_reward": round(
                best_rr,
                2,
            ),
            "bias": bias,
            "bias_strength": strength,
            "confidence": confidence,
            "bias_score": bias_score,
            "reasons": cls._deduplicate(
                reasons
            ),
            "invalidation": invalidation,
            "engine": "DETERMINISTIC",
        }

    # ==========================================================
    # ENTRY CANDIDATES
    # ==========================================================

    @classmethod
    def _build_entry_candidates(
        cls,
        *,
        direction: str,
        current_price: float,
        atr: float,
        latest_order_block: dict | None,
        latest_fvg: dict | None,
        latest_premium_discount: dict | None,
        support_resistance: dict | None,
    ) -> list[dict]:
        """
        Build directionally valid entry-zone candidates.
        """

        candidates: list[dict] = []

        # ------------------------------------------------------
        # Order Block
        # ------------------------------------------------------

        expected_ob_type = (
            "ORDER_BLOCK_BULLISH"
            if direction == "BUY"
            else "ORDER_BLOCK_BEARISH"
        )

        if (
            latest_order_block
            and latest_order_block.get("type")
            == expected_ob_type
        ):
            zone = cls._normalise_zone(
                latest_order_block.get(
                    "low_price"
                ),
                latest_order_block.get(
                    "high_price"
                ),
            )

            if zone:
                candidates.append(
                    cls._candidate(
                        source="ORDER_BLOCK",
                        low=zone[0],
                        high=zone[1],
                        current_price=current_price,
                        priority=1,
                    )
                )

        # ------------------------------------------------------
        # Fair Value Gap
        # ------------------------------------------------------

        expected_fvg_type = (
            "FVG_BULLISH"
            if direction == "BUY"
            else "FVG_BEARISH"
        )

        if (
            latest_fvg
            and latest_fvg.get("type")
            == expected_fvg_type
        ):
            zone = cls._normalise_zone(
                latest_fvg.get(
                    "lower_price"
                ),
                latest_fvg.get(
                    "upper_price"
                ),
            )

            if zone:
                candidates.append(
                    cls._candidate(
                        source="FVG",
                        low=zone[0],
                        high=zone[1],
                        current_price=current_price,
                        priority=2,
                    )
                )

        # ------------------------------------------------------
        # Support / Resistance
        # ------------------------------------------------------

        if support_resistance:
            zone_key = (
                "support_zones"
                if direction == "BUY"
                else "resistance_zones"
            )

            for item in (
                support_resistance.get(
                    zone_key,
                    []
                )
                or []
            ):
                zone = cls._normalise_zone(
                    item.get(
                        "lower_price"
                    ),
                    item.get(
                        "upper_price"
                    ),
                )

                if not zone:
                    continue

                candidates.append(
                    cls._candidate(
                        source=(
                            "SUPPORT"
                            if direction == "BUY"
                            else "RESISTANCE"
                        ),
                        low=zone[0],
                        high=zone[1],
                        current_price=current_price,
                        priority=3,
                    )
                )

        # ------------------------------------------------------
        # Premium / Discount
        #
        # This is deliberately lower priority than OB/FVG/SR.
        # ------------------------------------------------------

        if latest_premium_discount:

            if direction == "BUY":
                zone = cls._normalise_zone(
                    latest_premium_discount.get(
                        "discount_low"
                    ),
                    latest_premium_discount.get(
                        "discount_high"
                    ),
                )

                source = "DISCOUNT"

            else:
                zone = cls._normalise_zone(
                    latest_premium_discount.get(
                        "premium_low"
                    ),
                    latest_premium_discount.get(
                        "premium_high"
                    ),
                )

                source = "PREMIUM"

            if zone:
                candidates.append(
                    cls._candidate(
                        source=source,
                        low=zone[0],
                        high=zone[1],
                        current_price=current_price,
                        priority=4,
                    )
                )

        # ------------------------------------------------------
        # Reject absurdly distant candidates early.
        #
        # Keep a wider limit here than the final entry filter,
        # because candidate selection still needs alternatives.
        # ------------------------------------------------------

        maximum_candidate_distance = (
            atr * 5.0
        )

        return [
            candidate
            for candidate in candidates
            if candidate["distance"]
            <= maximum_candidate_distance
        ]

    @classmethod
    def _candidate(
        cls,
        *,
        source: str,
        low: float,
        high: float,
        current_price: float,
        priority: int,
    ) -> dict:
        """
        Build a normalized entry candidate.
        """

        preferred = (
            low
            + (
                high - low
            )
            / 2
        )

        return {
            "source": source,
            "low": low,
            "high": high,
            "preferred": preferred,
            "distance": cls._distance_to_zone(
                current_price,
                low,
                high,
            ),
            "priority": priority,
        }

    @staticmethod
    def _select_best_entry_candidate(
        candidates: list[dict],
        *,
        current_price: float,
    ) -> dict | None:
        """
        Prefer the closest candidate.

        Priority resolves equal-distance candidates.
        """

        _ = current_price

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda candidate: (
                candidate["distance"],
                candidate["priority"],
            ),
        )

    # ==========================================================
    # STOP LOSS
    # ==========================================================

    @classmethod
    def _calculate_stop_loss(
        cls,
        *,
        direction: str,
        entry_low: float,
        entry_high: float,
        atr: float,
        latest_order_block: dict | None,
        latest_liquidity_sweep: dict | None,
    ) -> float | None:
        """
        Place stop beyond the entry structure with an ATR buffer.

        When compatible order-block or liquidity-sweep structure
        exists, include that level in the invalidation boundary.
        """

        buffer_distance = (
            atr
            * cls.STOP_ATR_BUFFER
        )

        if direction == "BUY":

            structural_low = entry_low

            if (
                latest_order_block
                and latest_order_block.get(
                    "type"
                )
                == "ORDER_BLOCK_BULLISH"
            ):
                value = cls._safe_float(
                    latest_order_block.get(
                        "low_price"
                    )
                )

                if value is not None:
                    structural_low = min(
                        structural_low,
                        value,
                    )

            if (
                latest_liquidity_sweep
                and latest_liquidity_sweep.get(
                    "type"
                )
                == "LIQUIDITY_SWEEP_LOW"
            ):
                value = cls._safe_float(
                    latest_liquidity_sweep.get(
                        "level_price"
                    )
                )

                if value is not None:
                    structural_low = min(
                        structural_low,
                        value,
                    )

            return (
                structural_low
                - buffer_distance
            )

        if direction == "SELL":

            structural_high = entry_high

            if (
                latest_order_block
                and latest_order_block.get(
                    "type"
                )
                == "ORDER_BLOCK_BEARISH"
            ):
                value = cls._safe_float(
                    latest_order_block.get(
                        "high_price"
                    )
                )

                if value is not None:
                    structural_high = max(
                        structural_high,
                        value,
                    )

            if (
                latest_liquidity_sweep
                and latest_liquidity_sweep.get(
                    "type"
                )
                == "LIQUIDITY_SWEEP_HIGH"
            ):
                value = cls._safe_float(
                    latest_liquidity_sweep.get(
                        "level_price"
                    )
                )

                if value is not None:
                    structural_high = max(
                        structural_high,
                        value,
                    )

            return (
                structural_high
                + buffer_distance
            )

        return None

    # ==========================================================
    # TARGETS
    # ==========================================================

    @classmethod
    def _build_targets(
        cls,
        *,
        direction: str,
        entry: float,
        risk_distance: float,
        support_resistance: dict | None,
    ) -> list[dict]:
        """
        Build deterministic R-multiple targets.

        Nearby support/resistance may be used as an additional
        structural target when it lies in the correct direction.
        """

        targets: list[dict] = []

        for index, multiple in enumerate(
            cls.DEFAULT_TARGET_R_MULTIPLES,
            start=1,
        ):

            if direction == "BUY":
                price = (
                    entry
                    + risk_distance
                    * multiple
                )
            else:
                price = (
                    entry
                    - risk_distance
                    * multiple
                )

            targets.append(
                {
                    "name": f"TP{index}",
                    "price": cls._round_price(
                        price
                    ),
                    "rr": round(
                        multiple,
                        2,
                    ),
                    "source": "R_MULTIPLE",
                }
            )

        structural_target = (
            cls._find_structural_target(
                direction=direction,
                entry=entry,
                risk_distance=risk_distance,
                support_resistance=(
                    support_resistance
                ),
            )
        )

        if structural_target is not None:

            # Avoid duplicate target prices.
            duplicate = any(
                abs(
                    target["price"]
                    - structural_target["price"]
                )
                <= 1e-9
                for target in targets
            )

            if not duplicate:
                targets.append(
                    structural_target
                )

        targets.sort(
            key=lambda item: item["rr"]
        )

        return targets

    @classmethod
    def _find_structural_target(
        cls,
        *,
        direction: str,
        entry: float,
        risk_distance: float,
        support_resistance: dict | None,
    ) -> dict | None:
        """
        Find the nearest opposing support/resistance zone that
        lies beyond the entry.
        """

        if (
            not support_resistance
            or risk_distance <= 0
        ):
            return None

        if direction == "BUY":

            prices = []

            for zone in (
                support_resistance.get(
                    "resistance_zones",
                    []
                )
                or []
            ):
                value = cls._safe_float(
                    zone.get(
                        "center_price"
                    )
                )

                if (
                    value is not None
                    and value > entry
                ):
                    prices.append(
                        value
                    )

            if not prices:
                return None

            target_price = min(
                prices
            )

            reward = (
                target_price
                - entry
            )

        else:

            prices = []

            for zone in (
                support_resistance.get(
                    "support_zones",
                    []
                )
                or []
            ):
                value = cls._safe_float(
                    zone.get(
                        "center_price"
                    )
                )

                if (
                    value is not None
                    and value < entry
                ):
                    prices.append(
                        value
                    )

            if not prices:
                return None

            target_price = max(
                prices
            )

            reward = (
                entry
                - target_price
            )

        rr = (
            reward
            / risk_distance
        )

        if rr <= 0:
            return None

        return {
            "name": "STRUCTURE",
            "price": cls._round_price(
                target_price
            ),
            "rr": round(
                rr,
                2,
            ),
            "source": (
                "RESISTANCE"
                if direction == "BUY"
                else "SUPPORT"
            ),
        }

    # ==========================================================
    # STRUCTURE VALIDATION
    # ==========================================================

    @staticmethod
    def _find_structure_conflict(
        *,
        direction: str,
        latest_bos: dict | None,
        latest_choch: dict | None,
    ) -> str | None:
        """
        Reject obvious structural conflict.

        CHoCH is treated as particularly important because it may
        represent a recent character change against the bias.
        """

        if latest_choch:

            choch_type = (
                latest_choch.get(
                    "type"
                )
            )

            if (
                direction == "BUY"
                and choch_type
                == "CHOCH_BEARISH"
            ):
                return (
                    "Bearish CHoCH conflicts with the bullish trade direction."
                )

            if (
                direction == "SELL"
                and choch_type
                == "CHOCH_BULLISH"
            ):
                return (
                    "Bullish CHoCH conflicts with the bearish trade direction."
                )

        # BOS conflict is also rejected when no matching CHoCH
        # has already restored directional alignment.

        if latest_bos:

            bos_type = (
                latest_bos.get(
                    "type"
                )
            )

            if (
                direction == "BUY"
                and bos_type
                == "BOS_BEARISH"
                and (
                    not latest_choch
                    or latest_choch.get(
                        "type"
                    )
                    != "CHOCH_BULLISH"
                )
            ):
                return (
                    "Latest BOS is bearish and conflicts with the bullish trade direction."
                )

            if (
                direction == "SELL"
                and bos_type
                == "BOS_BULLISH"
                and (
                    not latest_choch
                    or latest_choch.get(
                        "type"
                    )
                    != "CHOCH_BEARISH"
                )
            ):
                return (
                    "Latest BOS is bullish and conflicts with the bearish trade direction."
                )

        return None

    @staticmethod
    def _collect_directional_confirmations(
        *,
        direction: str,
        latest_bos: dict | None,
        latest_choch: dict | None,
        latest_liquidity_sweep: dict | None,
    ) -> list[str]:

        reasons: list[str] = []

        if direction == "BUY":

            if (
                latest_bos
                and latest_bos.get(
                    "type"
                )
                == "BOS_BULLISH"
            ):
                reasons.append(
                    "Latest BOS confirms bullish structure."
                )

            if (
                latest_choch
                and latest_choch.get(
                    "type"
                )
                == "CHOCH_BULLISH"
            ):
                reasons.append(
                    "Bullish CHoCH supports the trade direction."
                )

            if (
                latest_liquidity_sweep
                and latest_liquidity_sweep.get(
                    "type"
                )
                == "LIQUIDITY_SWEEP_LOW"
            ):
                reasons.append(
                    "Low-side liquidity sweep supports a bullish reversal."
                )

        else:

            if (
                latest_bos
                and latest_bos.get(
                    "type"
                )
                == "BOS_BEARISH"
            ):
                reasons.append(
                    "Latest BOS confirms bearish structure."
                )

            if (
                latest_choch
                and latest_choch.get(
                    "type"
                )
                == "CHOCH_BEARISH"
            ):
                reasons.append(
                    "Bearish CHoCH supports the trade direction."
                )

            if (
                latest_liquidity_sweep
                and latest_liquidity_sweep.get(
                    "type"
                )
                == "LIQUIDITY_SWEEP_HIGH"
            ):
                reasons.append(
                    "High-side liquidity sweep supports a bearish reversal."
                )

        return reasons

    # ==========================================================
    # WAIT RESPONSE
    # ==========================================================

    @classmethod
    def _wait_result(
        cls,
        *,
        symbol: str | None,
        timeframe: str | None,
        current_price: float,
        market_bias: dict | None,
        reasons: list[str],
        direction: str | None = None,
        entry: dict | None = None,
        stop_loss: float | None = None,
        targets: list[dict] | None = None,
        risk_reward: float | None = None,
    ) -> dict:

        return {
            "status": "WAIT",
            "direction": direction,
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": cls._round_price(
                current_price
            ),
            "entry": entry,
            "stop_loss": stop_loss,
            "targets": (
                targets
                if targets is not None
                else []
            ),
            "risk_reward": risk_reward,
            "bias": cls._normalize_bias(
                market_bias
            ),
            "bias_strength": (
                cls._normalize_strength(
                    market_bias
                )
            ),
            "confidence": (
                cls._market_bias_number(
                    market_bias,
                    "confidence",
                )
            ),
            "bias_score": (
                cls._market_bias_number(
                    market_bias,
                    "score",
                )
            ),
            "reasons": cls._deduplicate(
                reasons
            ),
            "invalidation": None,
            "engine": "DETERMINISTIC",
        }

    # ==========================================================
    # HELPERS
    # ==========================================================

    @classmethod
    def _normalize_bias(
        cls,
        market_bias: dict | None,
    ) -> str | None:

        if not market_bias:
            return None

        value = market_bias.get(
            "bias"
        )

        if not isinstance(
            value,
            str,
        ):
            return None

        normalized = (
            value
            .strip()
            .upper()
        )

        if normalized not in cls.VALID_BIASES:
            return None

        return normalized

    @classmethod
    def _normalize_strength(
        cls,
        market_bias: dict | None,
    ) -> str | None:

        if not market_bias:
            return None

        value = market_bias.get(
            "strength"
        )

        if not isinstance(
            value,
            str,
        ):
            return None

        normalized = (
            value
            .strip()
            .upper()
            .replace(" ", "_")
        )

        if normalized not in cls.VALID_STRENGTHS:
            return None

        return normalized

    @staticmethod
    def _market_bias_number(
        market_bias: dict | None,
        key: str,
    ) -> float | None:

        if not market_bias:
            return None

        return (
            TradeSetupService
            ._safe_float(
                market_bias.get(
                    key
                )
            )
        )

    @staticmethod
    def _get_close_price(
        candle: Any,
    ) -> float | None:

        if hasattr(
            candle,
            "close_price",
        ):
            return (
                TradeSetupService
                ._safe_float(
                    candle.close_price
                )
            )

        if isinstance(
            candle,
            dict,
        ):
            return (
                TradeSetupService
                ._safe_float(
                    candle.get(
                        "close_price",
                        candle.get(
                            "close"
                        ),
                    )
                )
            )

        return None

    @staticmethod
    def _normalise_zone(
        first,
        second,
    ) -> tuple[float, float] | None:

        first_value = (
            TradeSetupService
            ._safe_float(
                first
            )
        )

        second_value = (
            TradeSetupService
            ._safe_float(
                second
            )
        )

        if (
            first_value is None
            or second_value is None
        ):
            return None

        low = min(
            first_value,
            second_value,
        )

        high = max(
            first_value,
            second_value,
        )

        if high <= low:
            return None

        return (
            low,
            high,
        )

    @staticmethod
    def _distance_to_zone(
        price: float,
        low: float,
        high: float,
    ) -> float:

        if low <= price <= high:
            return 0.0

        if price < low:
            return (
                low - price
            )

        return (
            price - high
        )

    @staticmethod
    def _safe_float(
        value,
    ) -> float | None:

        if value is None:
            return None

        if isinstance(
            value,
            bool,
        ):
            return None

        try:
            number = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ):
            return None

        if (
            number != number
            or number in (
                float("inf"),
                float("-inf"),
            )
        ):
            return None

        return number

    @classmethod
    def _positive_float(
        cls,
        value,
    ) -> float | None:

        number = cls._safe_float(
            value
        )

        if (
            number is None
            or number <= 0
        ):
            return None

        return number

    @staticmethod
    def _round_price(
        value: float,
    ) -> float:
        """
        Keep enough precision for FX while remaining safe for
        instruments such as JPY pairs and gold.

        Broker-specific digit formatting belongs to execution/UI.
        """

        return round(
            float(value),
            6,
        )

    @staticmethod
    def _deduplicate(
        values: list[str],
    ) -> list[str]:

        result = []
        seen = set()

        for value in values:

            if value in seen:
                continue

            seen.add(
                value
            )

            result.append(
                value
            )

        return result