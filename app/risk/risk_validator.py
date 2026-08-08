"""
risk_validator.py

Validates trade risk before approval.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from dataclasses import dataclass


@dataclass
class RiskValidationResult:
    """
    Stores risk validation result.
    """

    approved: bool
    reason: str


class RiskValidator:
    """
    Validate whether a trade follows
    risk management rules.
    """

    @staticmethod
    def validate(
        account_balance,
        risk_percent,
        trade_risk_amount,
        risk_reward=None,
        minimum_risk_reward=2,
    ):
        """
        Check trade safety.

        Rules:

        1. Risk amount must be within allowed percentage.
        2. Risk reward must be acceptable when provided.
        """

        allowed_risk = (
            account_balance
            * risk_percent
            / 100
        )

        # ==========================================
        # Check Maximum Risk Amount
        # ==========================================

        if trade_risk_amount > allowed_risk:

            return RiskValidationResult(
                approved=False,
                reason=(
                    "Trade risk exceeds "
                    "maximum allowed risk."
                ),
            )

        # ==========================================
        # Check Minimum Risk Reward
        # ==========================================

        if (
            risk_reward is not None
            and risk_reward < minimum_risk_reward
        ):

            return RiskValidationResult(
                approved=False,
                reason=(
                    "Trade risk reward is below "
                    "minimum required ratio."
                ),
            )

        # ==========================================
        # Trade Is Safe
        # ==========================================

        return RiskValidationResult(
            approved=True,
            reason=(
                "Trade risk is within allowed limit."
            ),
        )