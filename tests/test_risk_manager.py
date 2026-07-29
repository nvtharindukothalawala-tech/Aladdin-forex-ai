import pytest

from app.risk.risk_manager import RiskManager


def test_calculate_risk_amount():
    risk_amount = RiskManager.calculate_risk_amount(
        account_balance=10000,
        risk_percent=1,
    )

    assert risk_amount == pytest.approx(100)


def test_calculate_risk_amount_rejects_invalid_account_balance():
    with pytest.raises(
        ValueError,
        match="Account balance must be greater than zero.",
    ):
        RiskManager.calculate_risk_amount(
            account_balance=0,
            risk_percent=1,
        )


def test_calculate_risk_amount_rejects_invalid_risk_percent():
    with pytest.raises(
        ValueError,
        match="Risk percentage must be between 0 and 100.",
    ):
        RiskManager.calculate_risk_amount(
            account_balance=10000,
            risk_percent=0,
        )


def test_calculate_position_size():
    position_size = RiskManager.calculate_position_size(
        risk_amount=100,
        stop_loss_distance=0.0050,
    )

    assert position_size == pytest.approx(20000)


def test_calculate_position_size_rejects_zero_stop_loss_distance():
    with pytest.raises(
        ValueError,
        match="Stop loss distance must be greater than zero.",
    ):
        RiskManager.calculate_position_size(
            risk_amount=100,
            stop_loss_distance=0,
        )


def test_calculate_pips_for_eurusd():
    pips = RiskManager.calculate_pips(
        symbol="EUR/USD",
        price_distance=0.0050,
    )

    assert pips == pytest.approx(50)


def test_get_pip_size_for_eurusd():
    pip_size = RiskManager.get_pip_size("EUR/USD")

    assert pip_size == pytest.approx(0.0001)


def test_get_pip_size_for_usdjpy():
    pip_size = RiskManager.get_pip_size("USD/JPY")

    assert pip_size == pytest.approx(0.01)


def test_calculate_pips_for_usdjpy():
    pips = RiskManager.calculate_pips(
        symbol="USD/JPY",
        price_distance=0.50,
    )

    assert pips == pytest.approx(50)
