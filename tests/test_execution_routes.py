"""
test_execution_routes.py

Tests execution API endpoint.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


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

def test_ai_execution_api_runs_server_side_approval_workflow():
    """
    Test that AI execution uses Aladdin's
    internal analysis and approval workflow.
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
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"]["action"] == "BUY"

    assert data["approval"]["approved"] is True

    assert data["execution_result"]["status"] == "EXECUTED"

def test_ai_execution_api_blocks_high_risk_trade():
    """
    Test that AI execution does not execute
    when risk validation rejects the trade.
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
            "trade_risk_amount": 500,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"]["action"] == "BUY"

    assert data["approval"]["approved"] is False

    assert "execution_result" not in data

def test_ai_execution_api_does_not_execute_hold_decision():
    """
    Test that AI execution does not execute
    when the final decision is HOLD.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 50,
            "adx_value": 10,
            "volatility": "HIGH",
            "currency": "USD",
            "event_type": "Economic Report",
            "importance": "HIGH",
            "sentiment": "BEARISH",
            "price_structure": "RANGE",
            "liquidity_sweep": False,
            "order_block": "BEARISH",
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

    assert "approval" not in data

    assert "execution" not in data

    assert "execution_result" not in data

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