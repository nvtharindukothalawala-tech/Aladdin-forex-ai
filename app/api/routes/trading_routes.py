"""
trading_routes.py

Contains complete trading workflow API.

Author: Tharindu Kothalwala
Project: Aladdin
"""


from fastapi import APIRouter

from app.services.trading_service import (
    TradingService,
)

from app.schemas.trading_schema import (
    TradingRequest,
)


router = APIRouter(
    prefix="/trading",
    tags=["Trading Workflow"],
)


@router.post("/analyze")
def analyze_trade(
    data: TradingRequest,
):
    """
    Generate complete trade setup.
    """


    result = TradingService.generate_trade_setup(

        symbol=data.symbol,

        trend=data.trend,

        momentum=data.momentum,

        risk_reward=data.risk_reward,

        entry_price=data.entry_price,

        stop_loss=data.stop_loss,

        take_profit=data.take_profit,

        account_balance=data.account_balance,

        risk_percent=data.risk_percent,

        trade_risk_amount=data.trade_risk_amount,
    )


    return result