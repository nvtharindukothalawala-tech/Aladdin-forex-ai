"""
trade_planner.py

Creates structured trade plans.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.planning.trade_plan import TradePlan


class TradePlanner:
    """
    Create trade setups from trading decisions.
    """

    @staticmethod
    def create_plan(
        symbol,
        direction,
        entry_price,
        stop_loss,
        take_profit,
    ):
        """
        Create a trade plan.

        Calculates risk reward ratio.
        """

        if direction == "BUY":

            risk = entry_price - stop_loss

            reward = take_profit - entry_price

        else:

            risk = stop_loss - entry_price

            reward = entry_price - take_profit

        if risk <= 0:

            raise ValueError("Invalid stop loss placement.")

        risk_reward = reward / risk

        return TradePlan(
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward=round(
                risk_reward,
                2,
            ),
        )
