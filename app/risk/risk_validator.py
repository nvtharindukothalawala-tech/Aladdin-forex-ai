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
        minimum_risk_reward=2,
    ):
        """
        Check trade safety.

        Rules:

        1. Risk amount must be within allowed percentage.
        2. Risk reward must be acceptable.
        """

        allowed_risk = account_balance * risk_percent / 100

        if trade_risk_amount > allowed_risk:

            return RiskValidationResult(
                approved=False,
                reason=("Trade risk exceeds " "maximum allowed risk."),
            )

        return RiskValidationResult(
            approved=True,
            reason=("Trade risk is within " "allowed limit."),
        )
