"""
trading_service.py

Combines decision making,
trade planning, risk validation,
and execution preparation.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.decision.decision_engine import DecisionEngine

from app.planning.trade_planner import TradePlanner

from app.risk.risk_validator import RiskValidator

from app.execution.execution_manager import (
    ExecutionManager,
)


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
        lot_size,
    ):
        """
        Generate complete trading workflow.

        Steps:

        1. Decision generation
        2. Trade planning
        3. Risk validation
        4. Execution preparation
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

            risk_validation = RiskValidator.validate(
                account_balance=account_balance,
                risk_percent=risk_percent,
                trade_risk_amount=trade_risk_amount,
            )

            result["trade_plan"] = trade_plan

            result["risk_validation"] = risk_validation

            if risk_validation.approved:

                execution = ExecutionManager.prepare_execution(
                    symbol=symbol,
                    direction=decision.action,
                    lot_size=lot_size,
                    approved=True,
                )

                result["execution"] = execution

        return result
