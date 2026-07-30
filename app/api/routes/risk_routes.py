"""
risk_routes.py

Contains API endpoints related to
risk management calculations.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi import APIRouter

from app.risk.risk_manager import RiskManager
from app.schemas.risk_schema import (
    RiskCalculateSchema,
    LotSizeSchema,
    RiskRewardSchema,
)

router = APIRouter(
    prefix="/risk",
    tags=["Risk Management"],
)


@router.post("/calculate")
def calculate_risk(
    data: RiskCalculateSchema,
):
    """
    Calculate risk amount.
    """

    risk_amount = RiskManager.calculate_risk_amount(
        account_balance=data.account_balance,
        risk_percent=data.risk_percent,
    )

    return {
        "risk_amount": risk_amount,
    }


@router.post("/lot-size")
def calculate_lot_size(
    data: LotSizeSchema,
):
    """
    Calculate Forex lot size.
    """

    lot_size = RiskManager.calculate_forex_lot_size(
        risk_amount=data.risk_amount,
        stop_loss_pips=data.stop_loss_pips,
        pip_value=data.pip_value,
    )

    return {
        "lot_size": lot_size,
    }


@router.post("/risk-reward")
def calculate_risk_reward(
    data: RiskRewardSchema,
):
    """
    Calculate risk reward ratio.
    """

    ratio = RiskManager.calculate_risk_reward_ratio(
        entry_price=data.entry_price,
        stop_loss_price=data.stop_loss,
        take_profit_price=data.take_profit,
    )

    return {
        "risk_reward_ratio": ratio,
    }
