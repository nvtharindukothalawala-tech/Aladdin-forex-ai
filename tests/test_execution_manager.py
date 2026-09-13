"""
test_execution_manager.py

Tests trade execution request preparation
and MT5 correlation propagation.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from app.execution.execution_manager import (
    ExecutionManager,
)

from app.mt5.mt5_connector import (
    MT5ExecutionResult,
)


def test_prepare_execution_for_approved_trade():
    """
    Approved trades should produce
    a READY execution request.
    """

    request = ExecutionManager.prepare_execution(
        symbol="EUR/USD",
        direction="BUY",
        lot_size=0.10,
        approved=True,
    )

    assert request.symbol == "EUR/USD"
    assert request.order_type == "BUY"
    assert request.volume == 0.10
    assert request.status == "READY"

    assert request.entry_price is None
    assert request.stop_loss is None
    assert request.take_profit is None

    # Correlation ID is assigned later,
    # after the PENDING execution record
    # has been committed by ExecutionService.
    assert request.execution_id is None


def test_prepare_execution_rejects_unapproved_trade():
    """
    Unapproved trades must not be prepared
    for broker execution.
    """

    try:
        ExecutionManager.prepare_execution(
            symbol="EUR/USD",
            direction="BUY",
            lot_size=0.10,
            approved=False,
        )

        assert False, (
            "Expected unapproved trade "
            "to raise ValueError."
        )

    except ValueError as error:
        assert (
            str(error)
            == "Trade is not approved for execution."
        )


def test_execute_with_mt5_passes_execution_id_to_connector(
    monkeypatch,
):
    """
    Verify that the local execution ID
    reaches MT5Connector.prepare_order().
    """

    request = ExecutionManager.prepare_execution(
        symbol="EUR/USD",
        direction="BUY",
        lot_size=0.10,
        approved=True,
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1100,
    )

    request.execution_id = 123

    captured = {
        "execution_id": None,
        "connected": False,
        "disconnected": False,
    }

    class FakeConnector:
        def connect(self):
            captured["connected"] = True
            return True

        def prepare_order(
            self,
            symbol,
            order_type,
            volume,
            entry_price=None,
            stop_loss=None,
            take_profit=None,
            execution_id=None,
        ):
            captured["execution_id"] = execution_id

            class PreparedOrder:
                status = "READY"

            return PreparedOrder()

        def send_order(
            self,
            order,
        ):
            return MT5ExecutionResult(
                success=True,
                message=(
                    "Mock order executed successfully."
                ),
                order_id="MOCK_ORDER_001",
            )

        def disconnect(self):
            captured["disconnected"] = True

    monkeypatch.setattr(
        "app.execution.execution_manager.MT5Connector",
        FakeConnector,
    )

    result = ExecutionManager.execute_with_mt5(
        request
    )

    assert captured["connected"] is True

    assert (
        captured["execution_id"]
        == 123
    )

    assert (
        captured["disconnected"]
        is True
    )

    assert result.success is True

    assert (
        result.order_id
        == "MOCK_ORDER_001"
    )