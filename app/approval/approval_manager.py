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
    ):
        """
        Approve trade after risk validation.
        """

        if not risk_validation.approved:

            return ApprovalResult(
                approved=False,
                reason=risk_validation.reason,
            )

        return ApprovalResult(
            approved=True,
            reason="Trade approved.",
        )
