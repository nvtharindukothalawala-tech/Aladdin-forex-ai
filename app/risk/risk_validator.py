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
        """

        # ==================================
        # Basic Input Validation
        # ==================================

        if account_balance <= 0:

            return RiskValidationResult(
                approved=False,
                reason="Account balance must be positive.",
            )

        if risk_percent <= 0 or risk_percent > 100:

            return RiskValidationResult(
                approved=False,
                reason="Risk percentage must be between 0 and 100.",
            )

        if trade_risk_amount <= 0:

            return RiskValidationResult(
                approved=False,
                reason="Trade risk amount must be positive.",
            )

        allowed_risk = account_balance * risk_percent / 100

        # ==================================
        # Maximum Risk Check
        # ==================================

        if trade_risk_amount > allowed_risk:

            return RiskValidationResult(
                approved=False,
                reason=("Trade risk exceeds " "maximum allowed risk."),
            )

        # ==================================
        # Risk Reward Check
        # ==================================

        if risk_reward is not None and risk_reward < minimum_risk_reward:

            return RiskValidationResult(
                approved=False,
                reason=("Trade risk reward is below " "minimum required ratio."),
            )

        return RiskValidationResult(
            approved=True,
            reason=("Trade risk is within allowed limit."),
        )
