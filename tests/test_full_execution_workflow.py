"""
test_full_execution_workflow.py

Tests complete trading execution workflow.

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


def test_full_trade_execution_workflow():

    session = SessionLocal()

    repository = ExecutionRepository(session)

    execution_service = ExecutionService(repository)

    result = TradingService.generate_trade_setup(
        symbol="EUR/USD",
        trend="Bullish",
        momentum="Positive",
        risk_reward=3.0,
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1150,
        account_balance=10000,
        risk_percent=1,
        trade_risk_amount=100,
        lot_size=0.10,
        execute=True,
        execution_service=execution_service,
        user_id=1,
    )

    assert result["approval"].approved is True

    assert "execution_result" in result

    execution_result = result["execution_result"]

    assert execution_result.status == "EXECUTED"

    assert execution_result.broker_order_id == "MOCK_ORDER_001"

    session.close()
