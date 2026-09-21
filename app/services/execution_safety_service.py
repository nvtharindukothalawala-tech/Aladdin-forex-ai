"""
execution_safety_service.py

Deterministic pre-execution safety validation for Aladdin.

This service sits between an approved RiskService result and the
existing execution lifecycle. It does not send orders to MT5 and does
not modify broker state.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from __future__ import annotations

import math
import os
from typing import Any


class ExecutionSafetyService:
    """
    Validate a trade immediately before broker execution.

    The service is intentionally deterministic.

    It does NOT:
    - calculate position size
    - create trades
    - send MT5 orders
    - modify MT5 positions

    It only decides whether an already prepared trade is safe to pass
    into the existing execution lifecycle.
    """

    ENGINE = "DETERMINISTIC"

    DEFAULT_MAX_VOLUME = 10.0
    DEFAULT_MAX_SPREAD_STOP_RATIO = 0.25

    SUPPORTED_DIRECTIONS = {
        "BUY",
        "SELL",
    }

    SUPPORTED_EXECUTION_MODES = {
        "MOCK",
        "DEMO",
    }

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    @classmethod
    def analyze(
        cls,
        *,
        trade_setup: dict[str, Any] | None,
        risk: dict[str, Any] | None,
        quote: dict[str, Any] | None,
        symbol_info: dict[str, Any] | None,
        execution_mode: str | None = None,
        demo_execution_enabled: bool | None = None,
        max_volume: float | None = None,
        max_spread_stop_ratio: float | None = None,
    ) -> dict[str, Any]:
        """
        Run deterministic pre-execution safety checks.

        All checks are fail-closed. If required information is missing,
        execution is rejected.
        """

        checks: dict[str, str] = {
            "setup": "PENDING",
            "risk": "PENDING",
            "prices": "PENDING",
            "spread": "PENDING",
            "volume": "PENDING",
            "broker_volume": "PENDING",
            "environment": "PENDING",
        }

        reasons: list[str] = []

        mode = cls._normalize_execution_mode(
            execution_mode
        )

        if demo_execution_enabled is None:
            demo_execution_enabled = (
                cls._is_demo_execution_enabled()
            )

        configured_max_volume = (
            cls._resolve_positive_setting(
                supplied=max_volume,
                environment_name=(
                    "ALADDIN_MAX_EXECUTION_VOLUME"
                ),
                default=cls.DEFAULT_MAX_VOLUME,
            )
        )

        configured_spread_ratio = (
            cls._resolve_positive_setting(
                supplied=max_spread_stop_ratio,
                environment_name=(
                    "ALADDIN_MAX_SPREAD_STOP_RATIO"
                ),
                default=(
                    cls.DEFAULT_MAX_SPREAD_STOP_RATIO
                ),
            )
        )

        # ======================================================
        # 1. TRADE SETUP
        # ======================================================

        direction = cls._check_trade_setup(
            trade_setup=trade_setup,
            checks=checks,
            reasons=reasons,
        )

        # ======================================================
        # 2. RISK APPROVAL
        # ======================================================

        cls._check_risk(
            risk=risk,
            checks=checks,
            reasons=reasons,
        )

        # ======================================================
        # 3. PRICE STRUCTURE
        # ======================================================

        entry_price = cls._number_from(
            risk,
            "entry_price",
        )

        stop_loss = cls._number_from(
            risk,
            "stop_loss",
        )

        take_profit = (
            cls._extract_take_profit(
                trade_setup
            )
        )

        cls._check_price_structure(
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            checks=checks,
            reasons=reasons,
        )

        # ======================================================
        # 4. SPREAD VS STOP DISTANCE
        # ======================================================

        cls._check_spread(
            quote=quote,
            entry_price=entry_price,
            stop_loss=stop_loss,
            max_ratio=configured_spread_ratio,
            checks=checks,
            reasons=reasons,
        )

        # ======================================================
        # 5. ALADDIN VOLUME CAP
        # ======================================================

        volume = cls._number_from(
            risk,
            "volume",
        )

        cls._check_volume_cap(
            volume=volume,
            max_volume=configured_max_volume,
            checks=checks,
            reasons=reasons,
        )

        # ======================================================
        # 6. BROKER VOLUME RULES
        # ======================================================

        cls._check_broker_volume(
            volume=volume,
            symbol_info=symbol_info,
            checks=checks,
            reasons=reasons,
        )

        # ======================================================
        # 7. EXECUTION ENVIRONMENT
        # ======================================================

        cls._check_environment(
            execution_mode=mode,
            demo_execution_enabled=(
                demo_execution_enabled
            ),
            checks=checks,
            reasons=reasons,
        )

        # ======================================================
        # FINAL RESULT
        # ======================================================

        approved = (
            len(reasons) == 0
            and all(
                result == "PASS"
                for result in checks.values()
            )
        )

        return {
            "status": (
                "APPROVED"
                if approved
                else "REJECTED"
            ),
            "approved": approved,
            "engine": cls.ENGINE,
            "execution_mode": mode,
            "checks": checks,
            "reasons": reasons,
            "limits": {
                "max_volume": (
                    configured_max_volume
                ),
                "max_spread_stop_ratio": (
                    configured_spread_ratio
                ),
            },
        }

    # ==========================================================
    # SETUP CHECK
    # ==========================================================

    @classmethod
    def _check_trade_setup(
        cls,
        *,
        trade_setup,
        checks,
        reasons,
    ) -> str | None:
        if not isinstance(
            trade_setup,
            dict,
        ):
            checks["setup"] = "FAIL"
            reasons.append(
                "Trade setup is unavailable."
            )
            return None

        status = str(
            trade_setup.get(
                "status",
                "",
            )
        ).strip().upper()

        direction = str(
            trade_setup.get(
                "direction",
                "",
            )
        ).strip().upper()

        if status != "TRADE":
            checks["setup"] = "FAIL"
            reasons.append(
                "Trade setup is not executable."
            )
            return (
                direction
                if direction
                else None
            )

        if (
            direction
            not in cls.SUPPORTED_DIRECTIONS
        ):
            checks["setup"] = "FAIL"
            reasons.append(
                "Trade direction must be BUY or SELL."
            )
            return None

        checks["setup"] = "PASS"

        return direction

    # ==========================================================
    # RISK CHECK
    # ==========================================================

    @classmethod
    def _check_risk(
        cls,
        *,
        risk,
        checks,
        reasons,
    ):
        if not isinstance(
            risk,
            dict,
        ):
            checks["risk"] = "FAIL"
            reasons.append(
                "Risk analysis is unavailable."
            )
            return

        status = str(
            risk.get(
                "status",
                "",
            )
        ).strip().upper()

        approved = (
            risk.get("approved")
            is True
        )

        if (
            status != "APPROVED"
            or not approved
        ):
            checks["risk"] = "FAIL"
            reasons.append(
                "Risk analysis has not approved "
                "this trade."
            )
            return

        checks["risk"] = "PASS"

    # ==========================================================
    # PRICE CHECK
    # ==========================================================

    @classmethod
    def _check_price_structure(
        cls,
        *,
        direction,
        entry_price,
        stop_loss,
        take_profit,
        checks,
        reasons,
    ):
        if not all(
            cls._is_positive_number(value)
            for value in (
                entry_price,
                stop_loss,
                take_profit,
            )
        ):
            checks["prices"] = "FAIL"
            reasons.append(
                "Entry, stop loss and take profit "
                "must be positive."
            )
            return

        if direction == "BUY":
            valid = (
                stop_loss
                < entry_price
                < take_profit
            )

        elif direction == "SELL":
            valid = (
                take_profit
                < entry_price
                < stop_loss
            )

        else:
            valid = False

        if not valid:
            checks["prices"] = "FAIL"
            reasons.append(
                "Trade price structure is invalid."
            )
            return

        checks["prices"] = "PASS"

    # ==========================================================
    # SPREAD CHECK
    # ==========================================================

    @classmethod
    def _check_spread(
        cls,
        *,
        quote,
        entry_price,
        stop_loss,
        max_ratio,
        checks,
        reasons,
    ):
        if not isinstance(
            quote,
            dict,
        ):
            checks["spread"] = "FAIL"
            reasons.append(
                "Current market quote is unavailable."
            )
            return

        bid = cls._number_from(
            quote,
            "bid",
        )

        ask = cls._number_from(
            quote,
            "ask",
        )

        if not (
            cls._is_positive_number(bid)
            and cls._is_positive_number(ask)
            and ask >= bid
        ):
            checks["spread"] = "FAIL"
            reasons.append(
                "Current bid/ask quote is invalid."
            )
            return

        if not (
            cls._is_positive_number(entry_price)
            and cls._is_positive_number(stop_loss)
        ):
            checks["spread"] = "FAIL"
            reasons.append(
                "Stop distance cannot be validated."
            )
            return

        spread = ask - bid

        stop_distance = abs(
            entry_price - stop_loss
        )

        if stop_distance <= 0:
            checks["spread"] = "FAIL"
            reasons.append(
                "Stop distance must be greater than zero."
            )
            return

        spread_stop_ratio = (
            spread / stop_distance
        )

        if (
            spread_stop_ratio
            > max_ratio
        ):
            checks["spread"] = "FAIL"
            reasons.append(
                "Spread is too large relative "
                "to stop distance."
            )
            return

        checks["spread"] = "PASS"

    # ==========================================================
    # ALADDIN VOLUME CAP
    # ==========================================================

    @classmethod
    def _check_volume_cap(
        cls,
        *,
        volume,
        max_volume,
        checks,
        reasons,
    ):
        if not cls._is_positive_number(
            volume
        ):
            checks["volume"] = "FAIL"
            reasons.append(
                "Approved position volume is invalid."
            )
            return

        if volume > max_volume:
            checks["volume"] = "FAIL"
            reasons.append(
                "Position volume exceeds the "
                "configured Aladdin safety limit."
            )
            return

        checks["volume"] = "PASS"

    # ==========================================================
    # BROKER VOLUME CHECK
    # ==========================================================

    @classmethod
    def _check_broker_volume(
        cls,
        *,
        volume,
        symbol_info,
        checks,
        reasons,
    ):
        if not isinstance(
            symbol_info,
            dict,
        ):
            checks["broker_volume"] = "FAIL"
            reasons.append(
                "Broker symbol specifications "
                "are unavailable."
            )
            return

        volume_min = cls._number_from(
            symbol_info,
            "volume_min",
        )

        volume_max = cls._number_from(
            symbol_info,
            "volume_max",
        )

        volume_step = cls._number_from(
            symbol_info,
            "volume_step",
        )

        if not all(
            cls._is_positive_number(value)
            for value in (
                volume_min,
                volume_max,
                volume_step,
            )
        ):
            checks["broker_volume"] = "FAIL"
            reasons.append(
                "Broker volume specifications "
                "are invalid."
            )
            return

        if volume_min > volume_max:
            checks["broker_volume"] = "FAIL"
            reasons.append(
                "Broker volume range is invalid."
            )
            return

        if not cls._is_positive_number(
            volume
        ):
            checks["broker_volume"] = "FAIL"
            reasons.append(
                "Position volume cannot be validated "
                "against broker limits."
            )
            return

        tolerance = 1e-9

        if (
            volume < volume_min - tolerance
            or volume > volume_max + tolerance
        ):
            checks["broker_volume"] = "FAIL"
            reasons.append(
                "Position volume is outside "
                "broker limits."
            )
            return

        # RiskService should already normalize the
        # position to volume_step. We verify that
        # assumption again immediately before execution.

        steps = (
            (volume - volume_min)
            / volume_step
        )

        nearest_step = round(
            steps
        )

        if (
            abs(
                steps - nearest_step
            )
            > 1e-7
        ):
            checks["broker_volume"] = "FAIL"
            reasons.append(
                "Position volume does not match "
                "the broker volume step."
            )
            return

        checks["broker_volume"] = "PASS"

    # ==========================================================
    # ENVIRONMENT CHECK
    # ==========================================================

    @classmethod
    def _check_environment(
        cls,
        *,
        execution_mode,
        demo_execution_enabled,
        checks,
        reasons,
    ):
        if (
            execution_mode
            not in cls.SUPPORTED_EXECUTION_MODES
        ):
            checks["environment"] = "FAIL"
            reasons.append(
                "Unsupported execution mode. "
                "Only MOCK and DEMO are permitted."
            )
            return

        if (
            execution_mode == "DEMO"
            and demo_execution_enabled
            is not True
        ):
            checks["environment"] = "FAIL"
            reasons.append(
                "MT5 DEMO execution safety switch "
                "is disabled."
            )
            return

        checks["environment"] = "PASS"

    # ==========================================================
    # TAKE PROFIT EXTRACTION
    # ==========================================================

    @classmethod
    def _extract_take_profit(
        cls,
        trade_setup,
    ) -> float | None:
        """
        Select the first valid TP target.

        TradeSetupService currently exposes targets as
        a list of dictionaries containing price values.
        """

        if not isinstance(
            trade_setup,
            dict,
        ):
            return None

        targets = trade_setup.get(
            "targets"
        )

        if not isinstance(
            targets,
            list,
        ):
            return None

        # Prefer TP1 if the setup explicitly names it.

        for target in targets:
            if not isinstance(
                target,
                dict,
            ):
                continue

            name = str(
                target.get(
                    "name",
                    "",
                )
            ).strip().upper()

            price = cls._number_from(
                target,
                "price",
            )

            if (
                name == "TP1"
                and cls._is_positive_number(
                    price
                )
            ):
                return price

        # Otherwise use the first valid target price.

        for target in targets:
            if not isinstance(
                target,
                dict,
            ):
                continue

            price = cls._number_from(
                target,
                "price",
            )

            if cls._is_positive_number(
                price
            ):
                return price

        return None

    # ==========================================================
    # HELPERS
    # ==========================================================

    @staticmethod
    def _number_from(
        source,
        key,
    ) -> float | None:
        if not isinstance(
            source,
            dict,
        ):
            return None

        value = source.get(
            key
        )

        if value is None:
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

        if not math.isfinite(
            number
        ):
            return None

        return number

    @staticmethod
    def _is_positive_number(
        value,
    ) -> bool:
        return (
            isinstance(
                value,
                (int, float),
            )
            and not isinstance(
                value,
                bool,
            )
            and math.isfinite(
                float(value)
            )
            and float(value) > 0
        )

    @staticmethod
    def _normalize_execution_mode(
        execution_mode,
    ) -> str:
        if execution_mode is None:
            execution_mode = os.getenv(
                "ALADDIN_MT5_MODE",
                "MOCK",
            )

        return str(
            execution_mode
        ).strip().upper()

    @staticmethod
    def _is_demo_execution_enabled() -> bool:
        return (
            os.getenv(
                "ALADDIN_ENABLE_DEMO_EXECUTION",
                "false",
            )
            .strip()
            .lower()
            == "true"
        )

    @classmethod
    def _resolve_positive_setting(
        cls,
        *,
        supplied,
        environment_name,
        default,
    ) -> float:
        value = supplied

        if value is None:
            value = os.getenv(
                environment_name,
                str(default),
            )

        try:
            parsed = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ):
            return float(
                default
            )

        if not (
            math.isfinite(parsed)
            and parsed > 0
        ):
            return float(
                default
            )

        return parsed