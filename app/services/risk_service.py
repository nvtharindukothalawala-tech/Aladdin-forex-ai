"""Deterministic pre-trade risk engine for Aladdin."""

import math
from decimal import Decimal, ROUND_FLOOR


class RiskService:
    DEFAULT_RISK_PERCENT = 1.0
    MAX_RISK_PERCENT = 2.0

    @staticmethod
    def _positive(value):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(float(value))
            and float(value) > 0
        )

    @staticmethod
    def _rejected(reason, **values):
        result = {
            "status": "REJECTED",
            "approved": False,
            "reason": reason,
            "engine": "DETERMINISTIC",
        }
        result.update(values)
        return result

    @staticmethod
    def _normalize_volume_down(raw_volume, minimum, maximum, step):
        raw = Decimal(str(raw_volume))
        minimum_d = Decimal(str(minimum))
        maximum_d = Decimal(str(maximum))
        step_d = Decimal(str(step))

        capped = min(raw, maximum_d)
        if capped < minimum_d:
            return None

        steps = (
            (capped - minimum_d) / step_d
        ).to_integral_value(rounding=ROUND_FLOOR)

        normalized = minimum_d + steps * step_d
        if normalized < minimum_d:
            return None

        return float(min(normalized, maximum_d))

    @classmethod
    def analyze(
        cls,
        *,
        trade_setup,
        equity,
        trade_tick_size,
        trade_tick_value,
        volume_min,
        volume_max,
        volume_step,
        risk_percent=DEFAULT_RISK_PERCENT,
    ):
        if not isinstance(trade_setup, dict):
            return cls._rejected("Trade setup is required.")

        if trade_setup.get("status") != "TRADE":
            return cls._rejected(
                "Trade setup is not executable."
            )

        direction = str(
            trade_setup.get("direction") or ""
        ).strip().upper()

        if direction not in {"BUY", "SELL"}:
            return cls._rejected(
                "Trade direction must be BUY or SELL."
            )

        entry = trade_setup.get("entry")
        if not isinstance(entry, dict):
            return cls._rejected("Trade entry is missing.")

        entry_price = entry.get("preferred")
        stop_loss = trade_setup.get("stop_loss")

        if not cls._positive(entry_price):
            return cls._rejected(
                "Preferred entry price must be positive."
            )

        if not cls._positive(stop_loss):
            return cls._rejected(
                "Stop loss must be positive."
            )

        entry_price = float(entry_price)
        stop_loss = float(stop_loss)

        if direction == "BUY" and stop_loss >= entry_price:
            return cls._rejected(
                "BUY stop loss must be below entry."
            )

        if direction == "SELL" and stop_loss <= entry_price:
            return cls._rejected(
                "SELL stop loss must be above entry."
            )

        if not cls._positive(equity):
            return cls._rejected(
                "Account equity must be positive."
            )

        if not cls._positive(risk_percent):
            return cls._rejected(
                "Risk percent must be positive."
            )

        equity = float(equity)
        risk_percent = float(risk_percent)

        if risk_percent > cls.MAX_RISK_PERCENT:
            return cls._rejected(
                "Risk percent exceeds the "
                f"{cls.MAX_RISK_PERCENT:.2f}% safety limit."
            )

        risk_amount = equity * risk_percent / 100.0

        specs = {
            "trade_tick_size": trade_tick_size,
            "trade_tick_value": trade_tick_value,
            "volume_min": volume_min,
            "volume_max": volume_max,
            "volume_step": volume_step,
        }

        for name, value in specs.items():
            if not cls._positive(value):
                return cls._rejected(
                    f"Broker {name} must be positive."
                )

        trade_tick_size = float(trade_tick_size)
        trade_tick_value = float(trade_tick_value)
        volume_min = float(volume_min)
        volume_max = float(volume_max)
        volume_step = float(volume_step)

        if volume_min > volume_max:
            return cls._rejected(
                "Broker minimum volume exceeds maximum volume."
            )

        # Use Decimal for broker price/tick arithmetic.
        #
        # Binary floats can represent a value such as
        # 1.1000 - 1.0950 as slightly more than 0.005.
        # That tiny error can make an exact 0.20-lot result
        # appear slightly below 0.20 and then floor to 0.19.
        entry_decimal = Decimal(str(entry_price))
        stop_decimal = Decimal(str(stop_loss))
        tick_size_decimal = Decimal(str(trade_tick_size))
        tick_value_decimal = Decimal(str(trade_tick_value))
        risk_amount_decimal = Decimal(str(risk_amount))

        stop_distance_decimal = abs(
            entry_decimal - stop_decimal
        )

        if stop_distance_decimal <= 0:
            return cls._rejected(
                "Stop distance must be positive."
            )

        ticks_at_risk_decimal = (
            stop_distance_decimal
            / tick_size_decimal
        )

        loss_per_lot_decimal = (
            ticks_at_risk_decimal
            * tick_value_decimal
        )

        if loss_per_lot_decimal <= 0:
            return cls._rejected(
                "Calculated loss per lot is invalid."
            )

        raw_volume_decimal = (
            risk_amount_decimal
            / loss_per_lot_decimal
        )

        # Convert back to floats only after the financial
        # calculation has been completed with Decimal.
        stop_distance = float(stop_distance_decimal)
        ticks_at_risk = float(ticks_at_risk_decimal)
        loss_per_lot = float(loss_per_lot_decimal)
        raw_volume = float(raw_volume_decimal)

        volume = cls._normalize_volume_down(
            raw_volume,
            volume_min,
            volume_max,
            volume_step,
        )

        if volume is None:
            return cls._rejected(
                "Safe position size is below the broker minimum volume.",
                risk_percent=risk_percent,
                equity=equity,
                risk_amount=risk_amount,
                entry_price=entry_price,
                stop_loss=stop_loss,
                stop_distance=stop_distance,
                raw_volume=raw_volume,
            )

        estimated_loss = loss_per_lot * volume

        if estimated_loss > risk_amount + max(1e-9, risk_amount * 1e-9):
            return cls._rejected(
                "Normalized position size exceeds the risk budget."
            )

        return {
            "status": "APPROVED",
            "approved": True,
            "reason": "Trade fits the configured risk limits.",
            "symbol": trade_setup.get("symbol"),
            "timeframe": trade_setup.get("timeframe"),
            "direction": direction,
            "risk_percent": risk_percent,
            "equity": equity,
            "risk_amount": risk_amount,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "stop_distance": stop_distance,
            "trade_tick_size": trade_tick_size,
            "trade_tick_value": trade_tick_value,
            "ticks_at_risk": ticks_at_risk,
            "loss_per_lot": loss_per_lot,
            "raw_volume": raw_volume,
            "volume": volume,
            "estimated_loss": estimated_loss,
            "volume_min": volume_min,
            "volume_max": volume_max,
            "volume_step": volume_step,
            "engine": "DETERMINISTIC",
        }
