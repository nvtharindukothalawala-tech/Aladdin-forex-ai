"""
trading_service.py

Combines decision making,
trade planning, and risk validation.

Author: Tharindu Kothalwala
Project: Aladdin
"""


from app.decision.decision_engine import DecisionEngine
from app.planning.trade_planner import TradePlanner
from app.risk.risk_validator import RiskValidator


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
        account_balance,
        risk_percent,
        trade_risk_amount,
    ):
        """
        Generate complete trade setup.

        Workflow:

        1. Generate trading decision.
        2. Create trade plan.
        3. Validate risk.
        4. Return final result.
        """


        decision = DecisionEngine.make_decision(
            trend=trend,
            momentum=momentum,
            risk_reward=risk_reward,
        )


        result = {
            "decision": decision,
        }


        # Only create trade plan for BUY or SELL.
        if decision.action != "HOLD":

            trade_plan = TradePlanner.create_plan(
                symbol=symbol,
                direction=decision.action,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
            )


            risk_validation = RiskValidator.validate(
                account_balance=account_balance,
                risk_percent=risk_percent,
                trade_risk_amount=trade_risk_amount,
            )


            result["trade_plan"] = trade_plan

            result["risk_validation"] = risk_validation


        return result