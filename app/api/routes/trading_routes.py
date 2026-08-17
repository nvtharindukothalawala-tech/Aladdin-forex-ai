"""
trading_routes.py

Contains complete trading workflow API.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi import APIRouter

from app.services.trading_service import (
    TradingService,
)

from app.schemas.trading_schema import (
    TradingRequest,
)

from app.schemas.ai_trade_analysis_schema import (
    AITradeAnalysisRequest,
)


router = APIRouter(
    prefix="/trading",
    tags=["Trading Workflow"],
)


# ==========================================
# BASIC TRADE ANALYSIS
# ==========================================

@router.post("/analyze")
def analyze_trade(
    data: TradingRequest,
):
    """
    Generate complete basic trade setup.
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
        lot_size=data.lot_size,
    )

    return result


# ==========================================
# AI TRADE ANALYSIS
# ==========================================

@router.post("/ai-analyze")
def analyze_ai_trade(
    data: AITradeAnalysisRequest,
):
    """
    Generate an AI-powered trade setup
    without executing a trade.

    This endpoint performs:

    1. Market intelligence
    2. Intelligent decision
    3. Trade planning
    4. Risk validation
    5. Trade approval
    6. AI reasoning

    No MT5 execution is performed here.
    """

    result = TradingService.generate_ai_trade_setup(
        symbol=data.symbol,
        ema_signal=data.ema_signal,
        rsi_value=data.rsi_value,
        adx_value=data.adx_value,
        volatility=data.volatility,
        currency=data.currency,
        event_type=data.event_type,
        importance=data.importance,
        sentiment=data.sentiment,
        price_structure=data.price_structure,
        liquidity_sweep=data.liquidity_sweep,
        order_block=data.order_block,
        fair_value_gap=data.fair_value_gap,
        entry_price=data.entry_price,
        stop_loss=data.stop_loss,
        take_profit=data.take_profit,
        account_balance=data.account_balance,
        risk_percent=data.risk_percent,
        trade_risk_amount=data.trade_risk_amount,
        lot_size=data.lot_size,
    )

    return result