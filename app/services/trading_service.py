"""
trading_service.py

Combines market analysis,
decision making, and trade planning.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.decision.decision_engine import DecisionEngine
from app.planning.trade_planner import TradePlanner


class TradingService:
    """
    Coordinates the complete trading workflow.
    """

    @staticmethod
    def generate_trade_setup(
        symbol,
        trend,
        momentum,
        risk_reward,
        entry_price,
        stop_loss,
        take_profit,
    ):
        """
        Generate a complete trade setup.

        Workflow:

        1. Generate decision
        2. Create trade plan if decision is BUY/SELL
        3. Return final result
        """

        decision = DecisionEngine.make_decision(
            trend=trend,
            momentum=momentum,
            risk_reward=risk_reward,
        )

        result = {
            "decision": decision,
        }

        if decision.action != "HOLD":

            trade_plan = TradePlanner.create_plan(
                symbol=symbol,
                direction=decision.action,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
            )

            result["trade_plan"] = trade_plan

        return result
