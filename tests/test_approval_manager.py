"""
test_approval_manager.py

Tests trade approval management.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.approval.approval_manager import ApprovalManager
from app.risk.risk_validator import RiskValidationResult


def test_approval_preserves_risk_rejection_reason():
    """
    Test that rejected trade approval
    keeps the real risk validation reason.
    """

    risk_validation = RiskValidationResult(
        approved=False,
        reason=(
            "Trade risk reward is below "
            "minimum required ratio."
        ),
    )

    result = ApprovalManager.approve_trade(
        risk_validation
    )

    assert result.approved is False

    assert result.reason == (
        "Trade risk reward is below "
        "minimum required ratio."
    )