"""
approval_manager.py

Handles trade approval decisions.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from dataclasses import dataclass


@dataclass
class ApprovalResult:
    """
    Represents trade approval result.
    """

    approved: bool
    reason: str


class ApprovalManager:
    """
    Controls final trade approval.
    """

    @staticmethod
    def approve_trade(
        risk_validation,
        decision=None,
    ):
        """
        Approve trade after safety checks.
        """

        if risk_validation is None:

            return ApprovalResult(
                approved=False,
                reason="Risk validation missing.",
            )

        if not risk_validation.approved:

            return ApprovalResult(
                approved=False,
                reason=risk_validation.reason,
            )

        if decision is not None:

            if decision not in [
                "BUY",
                "SELL",
            ]:

                return ApprovalResult(
                    approved=False,
                    reason=("Invalid trading decision."),
                )

        return ApprovalResult(
            approved=True,
            reason="Trade approved.",
        )
