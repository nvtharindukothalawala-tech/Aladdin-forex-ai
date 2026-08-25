"""
risk_gate.py

Combines risk calculations and risk validation
for the Aladdin Decision Pipeline.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from app.risk.risk_gate_result import (
    RiskGateResult,
)

from app.risk.risk_manager import (
    RiskManager,
)

from app.risk.risk_validator import (
    RiskValidator,
)


class RiskGate:
    """
    Final risk-safety gate before trade approval.

    The Risk Gate reuses the existing:

    - RiskManager
    - RiskValidator

    It does not execute trades.
    It only determines whether the
    proposed trade satisfies risk rules.
    """

    @staticmethod
    def evaluate(
        symbol,
        account_balance,
        risk_percent,
        entry_price,
        stop_loss,
        take_profit,
        lot_size,
        pip_value,
    ):
        """
        Evaluate the risk of a proposed Forex trade.

        The Risk Gate checks:

        1. Account balance
        2. Risk percentage
        3. Maximum allowed risk
        4. Stop-loss distance
        5. Actual trade risk
        6. Risk/reward ratio
        7. Final risk validation
        """

        gates_passed = []
        gates_failed = []

        # ==========================================
        # Account Balance Gate
        # ==========================================

        if account_balance <= 0:

            return RiskGateResult(
                approved=False,
                risk_amount=0.0,
                risk_reward=0.0,
                reason=(
                    "Risk Gate blocked the trade because "
                    "account balance must be greater than zero."
                ),
                gates_passed=gates_passed,
                gates_failed=[
                    "account_balance",
                ],
            )

        gates_passed.append(
            "account_balance"
        )

        # ==========================================
        # Risk Percentage Gate
        # ==========================================

        if risk_percent <= 0 or risk_percent > 100:

            return RiskGateResult(
                approved=False,
                risk_amount=0.0,
                risk_reward=0.0,
                reason=(
                    "Risk Gate blocked the trade because "
                    "risk percentage must be between 0 and 100."
                ),
                gates_passed=gates_passed,
                gates_failed=[
                    "risk_percent",
                ],
            )

        gates_passed.append(
            "risk_percent"
        )

        # ==========================================
        # Lot Size Gate
        # ==========================================

        if lot_size <= 0:

            return RiskGateResult(
                approved=False,
                risk_amount=0.0,
                risk_reward=0.0,
                reason=(
                    "Risk Gate blocked the trade because "
                    "lot size must be greater than zero."
                ),
                gates_passed=gates_passed,
                gates_failed=[
                    "lot_size",
                ],
            )

        gates_passed.append(
            "lot_size"
        )

        # ==========================================
        # Pip Value Gate
        # ==========================================

        if pip_value <= 0:

            return RiskGateResult(
                approved=False,
                risk_amount=0.0,
                risk_reward=0.0,
                reason=(
                    "Risk Gate blocked the trade because "
                    "pip value must be greater than zero."
                ),
                gates_passed=gates_passed,
                gates_failed=[
                    "pip_value",
                ],
            )

        gates_passed.append(
            "pip_value"
        )

        # ==========================================
        # Calculate Maximum Allowed Risk
        # ==========================================

        try:

            maximum_allowed_risk = (
                RiskManager.calculate_risk_amount(
                    account_balance=account_balance,
                    risk_percent=risk_percent,
                )
            )

        except Exception as error:

            return RiskGateResult(
                approved=False,
                risk_amount=0.0,
                risk_reward=0.0,
                reason=(
                    f"Maximum risk calculation failed: {error}"
                ),
                gates_passed=gates_passed,
                gates_failed=[
                    "maximum_allowed_risk",
                ],
            )

        gates_passed.append(
            "maximum_allowed_risk"
        )

        # ==========================================
        # Calculate Stop Loss Distance
        # ==========================================

        try:

            stop_loss_distance = abs(
                entry_price - stop_loss
            )

            if stop_loss_distance <= 0:

                raise ValueError(
                    "Entry price and stop loss "
                    "cannot be equal."
                )

            stop_loss_pips = (
                RiskManager.calculate_pips(
                    symbol=symbol,
                    price_distance=stop_loss_distance,
                )
            )

        except Exception as error:

            return RiskGateResult(
                approved=False,
                risk_amount=round(
                    maximum_allowed_risk,
                    2,
                ),
                risk_reward=0.0,
                reason=(
                    f"Stop loss calculation failed: {error}"
                ),
                gates_passed=gates_passed,
                gates_failed=[
                    "stop_loss_distance",
                ],
            )

        if stop_loss_pips <= 0:

            return RiskGateResult(
                approved=False,
                risk_amount=round(
                    maximum_allowed_risk,
                    2,
                ),
                risk_reward=0.0,
                reason=(
                    "Risk Gate blocked the trade because "
                    "stop-loss distance is invalid."
                ),
                gates_passed=gates_passed,
                gates_failed=[
                    "stop_loss_distance",
                ],
            )

        gates_passed.append(
            "stop_loss_distance"
        )

        # ==========================================
        # Calculate Actual Trade Risk
        # ==========================================

        try:

            actual_trade_risk = (
                RiskManager.calculate_trade_risk(
                    stop_loss_pips=stop_loss_pips,
                    pip_value=pip_value,
                    lot_size=lot_size,
                )
            )

        except Exception as error:

            return RiskGateResult(
                approved=False,
                risk_amount=0.0,
                risk_reward=0.0,
                reason=(
                    f"Actual trade risk calculation failed: "
                    f"{error}"
                ),
                gates_passed=gates_passed,
                gates_failed=[
                    "actual_trade_risk",
                ],
            )

        actual_trade_risk = round(
            actual_trade_risk,
            2,
        )

        gates_passed.append(
            "actual_trade_risk"
        )

        # ==========================================
        # Maximum Risk Gate
        # ==========================================

        if actual_trade_risk > maximum_allowed_risk:

            gates_failed.append(
                "maximum_risk"
            )

            return RiskGateResult(
                approved=False,
                risk_amount=actual_trade_risk,
                risk_reward=0.0,
                reason=(
                    "Risk Gate blocked the trade because "
                    f"actual trade risk of "
                    f"${actual_trade_risk:.2f} exceeds "
                    f"the maximum allowed risk of "
                    f"${maximum_allowed_risk:.2f}."
                ),
                gates_passed=gates_passed,
                gates_failed=gates_failed,
            )

        gates_passed.append(
            "maximum_risk"
        )

        # ==========================================
        # Risk / Reward Calculation
        # ==========================================

        try:

            risk_reward = (
                RiskManager.calculate_risk_reward_ratio(
                    entry_price=entry_price,
                    stop_loss_price=stop_loss,
                    take_profit_price=take_profit,
                )
            )

            risk_reward = round(
                risk_reward,
                2,
            )

        except Exception as error:

            return RiskGateResult(
                approved=False,
                risk_amount=actual_trade_risk,
                risk_reward=0.0,
                reason=(
                    f"Risk/reward calculation failed: {error}"
                ),
                gates_passed=gates_passed,
                gates_failed=[
                    "risk_reward",
                ],
            )

        # ==========================================
        # Minimum Risk / Reward Gate
        # ==========================================

        minimum_risk_reward = 2.0

        if risk_reward < minimum_risk_reward:

            gates_failed.append(
                "risk_reward"
            )

            return RiskGateResult(
                approved=False,
                risk_amount=actual_trade_risk,
                risk_reward=risk_reward,
                reason=(
                    "Risk Gate blocked the trade because "
                    f"risk/reward ratio of "
                    f"{risk_reward:.2f} is below the "
                    f"minimum required ratio of "
                    f"{minimum_risk_reward:.1f}."
                ),
                gates_passed=gates_passed,
                gates_failed=gates_failed,
            )

        gates_passed.append(
            "risk_reward"
        )

        # ==========================================
        # Existing Risk Validator
        # ==========================================

        validation = RiskValidator.validate(
            account_balance=account_balance,
            risk_percent=risk_percent,
            trade_risk_amount=actual_trade_risk,
            risk_reward=risk_reward,
        )

        if not validation.approved:

            gates_failed.append(
                "risk_validation"
            )

            return RiskGateResult(
                approved=False,
                risk_amount=actual_trade_risk,
                risk_reward=risk_reward,
                reason=validation.reason,
                gates_passed=gates_passed,
                gates_failed=gates_failed,
            )

        gates_passed.append(
            "risk_validation"
        )

        # ==========================================
        # Final Risk Approval
        # ==========================================

        return RiskGateResult(
            approved=True,
            risk_amount=actual_trade_risk,
            risk_reward=risk_reward,
            reason=(
                "Risk Gate approved the trade. "
                f"Actual trade risk: "
                f"${actual_trade_risk:.2f}. "
                f"Maximum allowed risk: "
                f"${maximum_allowed_risk:.2f}. "
                f"Risk/reward: 1:{risk_reward:.2f}."
            ),
            gates_passed=gates_passed,
            gates_failed=[],
        )