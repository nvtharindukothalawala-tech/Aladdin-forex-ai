import pytest

from app.services.risk_service import RiskService


def setup(status="TRADE", direction="BUY", entry=1.1000, stop=1.0950):
    return {
        "status": status,
        "direction": direction,
        "symbol": "EURUSD",
        "timeframe": "H1",
        "entry": None if entry is None else {
            "type": "ZONE",
            "source": "SUPPORT",
            "low": entry - 0.0002,
            "high": entry + 0.0002,
            "preferred": entry,
        },
        "stop_loss": stop,
    }


def analyze(**changes):
    values = {
        "trade_setup": setup(),
        "equity": 10000.0,
        "trade_tick_size": 0.00001,
        "trade_tick_value": 1.0,
        "volume_min": 0.01,
        "volume_max": 100.0,
        "volume_step": 0.01,
        "risk_percent": 1.0,
    }
    values.update(changes)
    return RiskService.analyze(**values)


def test_valid_buy():
    result = analyze()
    assert result["status"] == "APPROVED"
    assert result["approved"] is True
    assert result["risk_amount"] == pytest.approx(100)
    assert result["volume"] == pytest.approx(0.20)
    assert result["estimated_loss"] <= result["risk_amount"]
    assert result["engine"] == "DETERMINISTIC"


def test_valid_sell():
    result = analyze(
        trade_setup=setup("TRADE", "SELL", 1.1000, 1.1050)
    )
    assert result["status"] == "APPROVED"
    assert result["direction"] == "SELL"
    assert result["volume"] == pytest.approx(0.20)


def test_wait_rejected():
    result = analyze(
        trade_setup=setup("WAIT", None, None, None)
    )
    assert result["status"] == "REJECTED"
    assert result["reason"] == "Trade setup is not executable."


def test_missing_entry_rejected():
    result = analyze(
        trade_setup=setup("TRADE", "BUY", None, 1.095)
    )
    assert result["reason"] == "Trade entry is missing."


def test_bad_buy_stop_rejected():
    result = analyze(
        trade_setup=setup("TRADE", "BUY", 1.1, 1.101)
    )
    assert result["reason"] == "BUY stop loss must be below entry."


def test_bad_sell_stop_rejected():
    result = analyze(
        trade_setup=setup("TRADE", "SELL", 1.1, 1.099)
    )
    assert result["reason"] == "SELL stop loss must be above entry."


@pytest.mark.parametrize("value", [0, -1, float("inf"), float("nan")])
def test_bad_equity_rejected(value):
    assert analyze(equity=value)["reason"] == (
        "Account equity must be positive."
    )


@pytest.mark.parametrize("value", [0, -1, float("inf"), float("nan")])
def test_bad_risk_percent_rejected(value):
    assert analyze(risk_percent=value)["reason"] == (
        "Risk percent must be positive."
    )


def test_risk_limit():
    result = analyze(risk_percent=2.01)
    assert result["status"] == "REJECTED"
    assert "2.00% safety limit" in result["reason"]


@pytest.mark.parametrize(
    "field",
    [
        "trade_tick_size",
        "trade_tick_value",
        "volume_min",
        "volume_max",
        "volume_step",
    ],
)
def test_bad_broker_spec(field):
    result = analyze(**{field: 0})
    assert result["status"] == "REJECTED"
    assert field in result["reason"]


def test_bad_volume_range():
    result = analyze(volume_min=1, volume_max=0.5)
    assert result["reason"] == (
        "Broker minimum volume exceeds maximum volume."
    )


def test_volume_rounds_down():
    result = analyze(
        trade_setup=setup("TRADE", "BUY", 1.1000, 1.0958)
    )
    assert result["raw_volume"] == pytest.approx(100 / 420)
    assert result["volume"] == pytest.approx(0.23)
    assert result["estimated_loss"] <= 100


def test_never_rounds_up():
    result = analyze(
        trade_setup=setup("TRADE", "BUY", 1.1000, 1.0958)
    )
    assert result["volume"] <= result["raw_volume"]
    assert result["estimated_loss"] <= result["risk_amount"]


def test_caps_at_broker_max():
    result = analyze(
        equity=1_000_000,
        trade_setup=setup("TRADE", "BUY", 1.1000, 1.0999),
        volume_max=5,
    )
    assert result["status"] == "APPROVED"
    assert result["raw_volume"] > 5
    assert result["volume"] == pytest.approx(5)


def test_below_minimum_rejected():
    result = analyze(
        equity=100,
        trade_setup=setup("TRADE", "BUY", 1.1, 1.0),
    )
    assert result["status"] == "REJECTED"
    assert "below the broker minimum" in result["reason"]


def test_default_risk_one_percent():
    result = RiskService.analyze(
        trade_setup=setup(),
        equity=10000,
        trade_tick_size=0.00001,
        trade_tick_value=1,
        volume_min=0.01,
        volume_max=100,
        volume_step=0.01,
    )
    assert result["risk_percent"] == pytest.approx(1)
    assert result["risk_amount"] == pytest.approx(100)


def test_deterministic():
    assert analyze() == analyze()
