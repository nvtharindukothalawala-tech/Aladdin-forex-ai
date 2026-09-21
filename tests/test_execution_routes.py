"""
test_execution_routes.py

Tests execution API endpoint.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.api.main import app
from app.auth.dependencies import get_current_user


client = TestClient(app)


# ==========================================
# Authentication Test Fixture
# ==========================================


@pytest.fixture(autouse=True)
def authenticated_execution_user():
    """
    Supply a deterministic authenticated user
    for existing execution route tests.

    Existing tests use user_id=1, so this fixture
    keeps those tests focused on execution,
    validation, approval, and response behavior.

    The override is removed after every test
    to prevent authentication state leaking
    into other test modules.
    """

    app.dependency_overrides[
        get_current_user
    ] = lambda: SimpleNamespace(
        id=1,
    )

    yield

    app.dependency_overrides.pop(
        get_current_user,
        None,
    )


def install_bullish_low_risk_intelligence(monkeypatch):
    """
    Install deterministic bullish, low-risk market intelligence
    for AI execution route tests.

    This keeps the API tests independent from live/current market
    conditions while still exercising Aladdin's real Decision Gate,
    risk validation, approval, and execution workflow.
    """

    class FakeIntelligence(BaseModel):
        market_bias: str
        confidence: float

        technical_summary: str
        news_summary: str
        structure_summary: str

        risk_level: str
        recommendation: str

        structure_direction: str
        structure_confirmation: str

        timeframe_alignment: str
        timeframe_confidence: float
        timeframe_summary: str

        market_session: str
        session_activity: str
        session_condition: str
        session_summary: str

    fake_intelligence = FakeIntelligence(
        market_bias="BULLISH",
        confidence=82.0,

        technical_summary=(
            "Technical analysis supports a bullish setup."
        ),
        news_summary=(
            "News conditions are supportive."
        ),
        structure_summary=(
            "Market structure confirms bullish continuation."
        ),

        risk_level="LOW",
        recommendation="Bullish opportunity",

        structure_direction="BULLISH",
        structure_confirmation="BOS_BULLISH",

        timeframe_alignment="FULL",
        timeframe_confidence=100.0,
        timeframe_summary=(
            "Higher and lower timeframes are aligned bullish."
        ),

        market_session="LONDON",
        session_activity="HIGH",
        session_condition="FAVORABLE",
        session_summary=(
            "London session activity is favorable."
        ),
    )

    fake_analysis_result = {
        "intelligence": fake_intelligence,
    }

    class FakeMarketIntelligenceService:
        def analyze(self, symbol):
            return fake_analysis_result

        def close(self):
            pass

    monkeypatch.setattr(
        "app.services.trading_service.MarketIntelligenceService",
        FakeMarketIntelligenceService,
    )


def test_execute_trade_api():
    """
    Test successful approved trade execution.
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.10,
            "approved": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "EUR/USD"

    assert data["direction"] == "BUY"

    assert data["volume"] == 0.10

    assert data["status"] == "EXECUTED"

    assert data["broker_order_id"] == "MOCK_ORDER_001"


def test_execution_api_rejects_unapproved_trade():
    """
    Test that execution API cannot
    execute an unapproved trade.
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.10,
            "approved": False,
        },
    )

    assert response.status_code == 403

# ==========================================================
# DIRECT EXECUTION PRICE STRUCTURE
# ==========================================================


def test_execute_trade_api_accepts_complete_buy_price_structure(
    monkeypatch,
):
    """
    Direct BUY execution must forward Entry,
    Stop Loss and Take Profit to
    ExecutionManager.
    """

    from app.api.routes import (
        execution_routes,
    )

    captured = {}

    original_prepare_execution = (
        execution_routes
        .ExecutionManager
        .prepare_execution
    )

    def capture_prepare_execution(
        *args,
        **kwargs,
    ):
        captured.update(
            kwargs
        )

        return original_prepare_execution(
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        execution_routes.ExecutionManager,
        "prepare_execution",
        capture_prepare_execution,
    )

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.20,
            "approved": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1100,
        },
    )

    assert response.status_code == 200

    assert (
        captured["symbol"]
        == "EUR/USD"
    )

    assert (
        captured["direction"]
        == "BUY"
    )

    assert (
        captured["lot_size"]
        == 0.20
    )

    assert (
        captured["approved"]
        is True
    )

    assert (
        captured["entry_price"]
        == 1.1000
    )

    assert (
        captured["stop_loss"]
        == 1.0950
    )

    assert (
        captured["take_profit"]
        == 1.1100
    )


def test_execute_trade_api_accepts_complete_sell_price_structure(
    monkeypatch,
):
    """
    Direct SELL execution must forward Entry,
    Stop Loss and Take Profit to
    ExecutionManager.
    """

    from app.api.routes import (
        execution_routes,
    )

    captured = {}

    original_prepare_execution = (
        execution_routes
        .ExecutionManager
        .prepare_execution
    )

    def capture_prepare_execution(
        *args,
        **kwargs,
    ):
        captured.update(
            kwargs
        )

        return original_prepare_execution(
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        execution_routes.ExecutionManager,
        "prepare_execution",
        capture_prepare_execution,
    )

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "SELL",
            "volume": 0.20,
            "approved": True,
            "entry_price": 1.1000,
            "stop_loss": 1.1050,
            "take_profit": 1.0900,
        },
    )

    assert response.status_code == 200

    assert (
        captured["direction"]
        == "SELL"
    )

    assert (
        captured["entry_price"]
        == 1.1000
    )

    assert (
        captured["stop_loss"]
        == 1.1050
    )

    assert (
        captured["take_profit"]
        == 1.0900
    )


def test_execute_trade_api_rejects_partial_price_structure():
    """
    Entry, Stop Loss and Take Profit must
    always be supplied together.
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.20,
            "approved": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
        },
    )

    assert response.status_code == 403

    data = response.json()

    assert (
        "must be supplied together"
        in data["detail"]
    )


def test_execute_trade_api_rejects_entry_without_sl_tp():
    """
    Entry alone must not be accepted.
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.20,
            "approved": True,
            "entry_price": 1.1000,
        },
    )

    assert response.status_code == 403

    assert (
        "must be supplied together"
        in response.json()["detail"]
    )


def test_execute_trade_api_rejects_stop_loss_without_other_prices():
    """
    Stop Loss alone must not be accepted.
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.20,
            "approved": True,
            "stop_loss": 1.0950,
        },
    )

    assert response.status_code == 403

    assert (
        "must be supplied together"
        in response.json()["detail"]
    )


def test_execute_trade_api_rejects_take_profit_without_other_prices():
    """
    Take Profit alone must not be accepted.
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.20,
            "approved": True,
            "take_profit": 1.1100,
        },
    )

    assert response.status_code == 403

    assert (
        "must be supplied together"
        in response.json()["detail"]
    )


def test_execute_trade_api_rejects_invalid_buy_price_structure():
    """
    BUY structure must satisfy:

        stop_loss < entry_price < take_profit
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.20,
            "approved": True,
            "entry_price": 1.1000,
            "stop_loss": 1.1050,
            "take_profit": 1.1100,
        },
    )

    assert response.status_code == 403

    assert (
        "Invalid BUY price structure"
        in response.json()["detail"]
    )


def test_execute_trade_api_rejects_invalid_sell_price_structure():
    """
    SELL structure must satisfy:

        take_profit < entry_price < stop_loss
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "SELL",
            "volume": 0.20,
            "approved": True,
            "entry_price": 1.1000,

            # Invalid for SELL because SL
            # must be ABOVE entry.
            "stop_loss": 1.0950,

            "take_profit": 1.0900,
        },
    )

    assert response.status_code == 403

    assert (
        "Invalid SELL price structure"
        in response.json()["detail"]
    )


def test_execute_trade_api_without_prices_remains_backward_compatible():
    """
    Existing direct execution requests that do
    not supply Entry, SL or TP must continue
    working.
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.10,
            "approved": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["symbol"]
        == "EUR/USD"
    )

    assert (
        data["direction"]
        == "BUY"
    )

    assert (
        data["volume"]
        == 0.10
    )

    assert (
        data["status"]
        == "EXECUTED"
    )
    
def test_ai_execution_api_runs_server_side_approval_workflow(
    monkeypatch,
):
    """
    Test that AI execution uses Aladdin's
    internal analysis and approval workflow.
    """

    install_bullish_low_risk_intelligence(
        monkeypatch,
    )

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"]["action"] == "BUY"

    assert data["approval"]["approved"] is True

    assert data["execution_result"]["status"] == "EXECUTED"


def test_ai_execution_api_blocks_high_risk_trade(
    monkeypatch,
):
    """
    Test that AI execution does not execute
    when risk validation rejects the trade.
    """

    install_bullish_low_risk_intelligence(
        monkeypatch,
    )

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 500,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"]["action"] == "BUY"

    assert data["approval"]["approved"] is False

    assert "execution_result" not in data


def test_ai_execution_api_does_not_execute_hold_decision(monkeypatch):
    """
    Test that AI execution does not execute
    when backend market intelligence causes
    the Decision Gate to return HOLD.
    """

    class FakeIntelligence(BaseModel):
        market_bias: str
        confidence: float
        risk_level: str
        recommendation: str
        structure_direction: str
        structure_confirmation: str
        timeframe_alignment: str
        timeframe_confidence: float
        market_session: str
        session_activity: str
        session_condition: str

    fake_intelligence = FakeIntelligence(
        market_bias="BULLISH",
        confidence=80.0,
        risk_level="MEDIUM",
        recommendation="Wait",
        structure_direction="BULLISH",
        structure_confirmation="BOS_BULLISH",
        timeframe_alignment="FULL",
        timeframe_confidence=100.0,
        market_session="LONDON",
        session_activity="HIGH",
        session_condition="FAVORABLE",
    )

    fake_analysis_result = {
        "intelligence": fake_intelligence,
    }

    class FakeMarketIntelligenceService:
        def analyze(self, symbol):
            return fake_analysis_result

        def close(self):
            pass

    monkeypatch.setattr(
        "app.services.trading_service.MarketIntelligenceService",
        FakeMarketIntelligenceService,
    )

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "NEUTRAL",
            "rsi_value": 50,
            "adx_value": 0,
            "volatility": "NORMAL",
            "currency": "EUR",
            "event_type": "Backend Market Analysis",
            "importance": "LOW",
            "sentiment": "NEUTRAL",
            "price_structure": "RANGE",
            "liquidity_sweep": False,
            "order_block": "BULLISH",
            "fair_value_gap": False,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"]["action"] == "HOLD"
    assert data["decision"]["approved"] is False
    assert "risk_level" in data["decision"]["gates_failed"]

    assert "approval" not in data or data["approval"] is None
    assert "execution" not in data or data["execution"] is None
    assert "execution_result" not in data or data["execution_result"] is None


def test_ai_execution_api_rejects_invalid_lot_size():
    """
    Test that AI execution API rejects
    zero or negative lot size.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_invalid_account_balance():
    """
    Test that AI execution API rejects
    zero or negative account balance.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 0,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_invalid_risk_percent():
    """
    Test that AI execution API rejects
    invalid risk percentage values.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 0,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_invalid_trade_risk_amount():
    """
    Test that AI execution API rejects
    zero or negative trade risk amount.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 0,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_invalid_entry_price():
    """
    Test that AI execution API rejects
    zero or negative entry price.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 0,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_invalid_stop_loss():
    """
    Test that AI execution API rejects
    zero or negative stop loss.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 0,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_invalid_take_profit():
    """
    Test that AI execution API rejects
    zero or negative take profit.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 0,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_empty_symbol():
    """
    Test that AI execution API rejects
    an empty trading symbol.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_invalid_ema_signal():
    """
    Test that AI execution API rejects
    an unsupported EMA signal.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "UNKNOWN",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_invalid_volatility():
    """
    Test that AI execution API rejects
    unsupported volatility values.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "EXTREME",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_invalid_importance():
    """
    Test that AI execution API rejects
    unsupported news importance values.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "CRITICAL",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_invalid_sentiment():
    """
    Test that AI execution API rejects
    unsupported news sentiment values.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "POSITIVE",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_invalid_price_structure():
    """
    Test that AI execution API rejects
    unsupported price structure values.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "UNKNOWN",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_invalid_order_block():
    """
    Test that AI execution API rejects
    unsupported order block values.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "UNKNOWN",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_invalid_rsi_value():
    """
    Test that AI execution API rejects
    RSI values outside the 0 to 100 range.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 150,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_invalid_adx_value():
    """
    Test that AI execution API rejects
    ADX values outside the 0 to 100 range.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 150,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_empty_currency():
    """
    Test that AI execution API rejects
    an empty currency value.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_empty_event_type():
    """
    Test that AI execution API rejects
    an empty event type.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_invalid_user_id():
    """
    Test that AI execution API rejects
    zero or negative user IDs.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 0,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_whitespace_symbol():
    """
    Test that AI execution API rejects
    a symbol containing only whitespace.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "   ",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_whitespace_currency():
    """
    Test that AI execution API rejects
    a currency containing only whitespace.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "   ",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_ai_execution_api_rejects_whitespace_event_type():
    """
    Test that AI execution API rejects
    an event type containing only whitespace.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "   ",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 422


def test_execution_api_rejects_invalid_user_id():
    """
    Test that direct execution API rejects
    zero or negative user IDs.
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 0,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.10,
            "approved": True,
        },
    )

    assert response.status_code == 422


def test_execution_api_rejects_whitespace_symbol():
    """
    Test that direct execution API rejects
    a whitespace-only symbol.
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "   ",
            "direction": "BUY",
            "volume": 0.10,
            "approved": True,
        },
    )

    assert response.status_code == 422


def test_execution_api_rejects_invalid_direction():
    """
    Test that direct execution API rejects
    unsupported trade directions.
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "LONG",
            "volume": 0.10,
            "approved": True,
        },
    )

    assert response.status_code == 422


def test_execution_api_rejects_invalid_volume():
    """
    Test that direct execution API rejects
    zero or negative trade volume.
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0,
            "approved": True,
        },
    )

    assert response.status_code == 422


def test_execution_history_rejects_invalid_user_id():
    """
    Test that execution history API rejects
    invalid user IDs.
    """

    response = client.get(
        "/execution/history/0"
    )

    assert response.status_code == 422


def test_execution_statistics_rejects_invalid_user_id():
    """
    Test that execution statistics API rejects
    invalid user IDs.
    """

    response = client.get(
        "/execution/statistics/0"
    )

    assert response.status_code == 422


def test_ai_execution_response_schema_contains_reasoning():
    """
    Verify that the AI execution response
    supports the explainable reasoning field.
    """

    from app.schemas.execution_schema import (
        AIExecutionResponseSchema,
    )

    response = AIExecutionResponseSchema(
        decision={
            "action": "BUY",
        },
        reasoning={
            "decision": "BUY",
            "confidence": 85,
            "technical_reasons": [
                "EMA trend confirms bullish momentum."
            ],
            "structure_reasons": [
                "Liquidity sweep detected."
            ],
            "risk_reasons": [
                "Risk validation passed."
            ],
            "final_message": (
                "BUY decision generated."
            ),
        },
    )

    assert response.decision is not None
    assert response.reasoning is not None


def test_ai_execution_response_schema_supports_execution_result():
    """
    Verify that execution information can be
    returned by the AI execution response.
    """

    from app.schemas.execution_schema import (
        AIExecutionResponseSchema,
    )

    response = AIExecutionResponseSchema(
        decision={
            "action": "BUY",
        },
        approval={
            "approved": True,
        },
        execution={
            "symbol": "EUR/USD",
            "order_type": "BUY",
            "volume": 0.10,
            "status": "READY",
        },
        execution_result={
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.10,
            "status": "EXECUTED",
            "broker_order_id": "TEST-001",
        },
    )

    assert response.approval is not None
    assert response.execution is not None
    assert response.execution_result is not None

    assert (
        response.execution_result.symbol
        == "EUR/USD"
    )

    assert (
        response.execution_result.direction
        == "BUY"
    )

    assert (
        response.execution_result.volume
        == 0.10
    )

    assert (
        response.execution_result.status
        == "EXECUTED"
    )

    assert (
        response.execution_result.broker_order_id
        == "TEST-001"
    )

