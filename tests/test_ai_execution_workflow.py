"""
test_ai_execution_workflow.py

Tests complete AI execution workflow.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.database.connection import SessionLocal


from app.execution.repository import (
    ExecutionRepository,
)


from app.services.execution_service import (
    ExecutionService,
)


from app.services.trading_service import (
    TradingService,
)


def test_ai_execution_workflow():

    session = SessionLocal()

    repository = ExecutionRepository(session)

    execution_service = ExecutionService(repository)

    result = TradingService.generate_ai_execution_workflow(
        symbol="EUR/USD",
        # ==========================
        # Technical Agent Inputs
        # ==========================
        ema_signal="BULLISH",
        rsi_value=65,
        adx_value=30,
        volatility="NORMAL",
        # ==========================
        # News Agent Inputs
        # ==========================
        currency="USD",
        event_type="Interest Rate Decision",
        importance="HIGH",
        sentiment="BULLISH",
        # ==========================
        # Market Structure Agent Inputs
        # ==========================
        price_structure="BOS_BULLISH",
        liquidity_sweep=True,
        order_block="BULLISH",
        fair_value_gap=True,
        # ==========================
        # Trade Parameters
        # ==========================
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1150,
        # ==========================
        # Risk Parameters
        # ==========================
        account_balance=10000,
        risk_percent=1,
        trade_risk_amount=100,
        lot_size=0.10,
        # ==========================
        # Execution
        # ==========================
        execute=True,
        execution_service=execution_service,
        user_id=1,
    )

    # AI Decision validation

    assert result["decision"].action == "BUY"

    # Risk approval validation

    assert result["approval"].approved is True

    # Execution validation

    assert "execution_result" in result

    assert result["execution_result"].status == "EXECUTED"

    assert result["execution_result"].broker_order_id == "MOCK_ORDER_001"

    # Database cleanup

    session.close()
