"""
test_mt5_journal_sync.py

Tests MT5 completed-trade synchronization
with the database-backed journal service.

These tests use:
- Fake broker history
- In-memory SQLite database
- No real MT5 order execution

Author: Tharindu Kothalawala
Project: Aladdin
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.models import Base
from app.auth.models import UserModel
from app.database.repository import TradeRepository
from app.services.journal_service import JournalService
from app.services.broker_service import BrokerService


# ======================================================
# TEST DATABASE
# ======================================================

def create_test_session():
    """
    Create an isolated in-memory SQLite database.

    This does not modify the real Aladdin database.
    """

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False
        },
        poolclass=StaticPool,
    )

    Base.metadata.create_all(
        bind=engine
    )

    TestSession = sessionmaker(
        bind=engine
    )

    session = TestSession()

    user = UserModel(
        username="mt5journaltest",
        email="mt5journaltest@example.com",
        password_hash="test_hash",
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return session, user


# ======================================================
# FAKE ALADDIN MT5 HISTORY
# ======================================================

def fake_aladdin_history():
    """
    Return one fake completed Aladdin MT5 position.
    """

    return {
        "execution_mode": "DEMO",
        "connected": True,
        "history_days": 30,
        "closed_trade_count": 1,
        "total_profit": 20.0,
        "total_commission": -1.0,
        "total_swap": -0.5,
        "total_fee": 0.0,
        "total_net_profit": 18.5,
        "closed_trades": [
            {
                "deal_ticket": 900000001,
                "order_ticket": 900000002,
                "position_id": 900000003,
                "symbol": "EURUSD",
                "direction": "BUY",
                "volume": 0.01,
                "close_price": 1.16500,
                "profit": 20.0,
                "commission": -1.0,
                "swap": -0.5,
                "fee": 0.0,
                "net_profit": 18.5,
                "time": "2026-09-12T10:30:00",
                "magic": 20260911,
                "comment": "ALADDIN DEMO",
                "is_aladdin_trade": True,
            }
        ],
        "message": (
            "Fake MT5 completed-position history."
        ),
    }


# ======================================================
# TEST 1
# FIRST SYNC IMPORTS COMPLETED ALADDIN TRADE
# ======================================================

def test_mt5_sync_imports_completed_aladdin_trade(
    monkeypatch,
):
    session, user = create_test_session()

    try:
        monkeypatch.setattr(
            BrokerService,
            "get_trade_history",
            lambda days=30: fake_aladdin_history(),
        )

        repository = TradeRepository(
            session
        )

        service = JournalService(
            repository
        )

        result = service.sync_mt5_closed_trades(
            user_id=user.id,
            days=30,
        )

        assert result["imported_count"] == 1

        assert result["duplicate_count"] == 0

        assert result["skipped_count"] == 0

        trades = repository.get_user_trades(
            user.id
        )

        assert len(trades) == 1

        trade = trades[0]

        assert trade.symbol == "EURUSD"

        assert trade.direction == "BUY"

        assert trade.source == "MT5"

        assert trade.mt5_deal_ticket == 900000001

        assert trade.mt5_order_ticket == 900000002

        assert trade.mt5_position_id == 900000003

        assert trade.close_price == 1.16500

        assert trade.profit_loss == 18.5

        assert trade.result == "WIN"

        assert trade.risk_reward is None

        assert trade.is_aladdin_trade == 1

    finally:
        session.close()


# ======================================================
# TEST 2
# SECOND SYNC DOES NOT CREATE DUPLICATE
# ======================================================

def test_mt5_sync_prevents_duplicate_trade(
    monkeypatch,
):
    session, user = create_test_session()

    try:
        monkeypatch.setattr(
            BrokerService,
            "get_trade_history",
            lambda days=30: fake_aladdin_history(),
        )

        repository = TradeRepository(
            session
        )

        service = JournalService(
            repository
        )

        first_result = (
            service.sync_mt5_closed_trades(
                user_id=user.id,
                days=30,
            )
        )

        second_result = (
            service.sync_mt5_closed_trades(
                user_id=user.id,
                days=30,
            )
        )

        assert first_result["imported_count"] == 1

        assert second_result["imported_count"] == 0

        assert second_result["duplicate_count"] == 1

        trades = repository.get_user_trades(
            user.id
        )

        assert len(trades) == 1

        assert (
            trades[0].mt5_deal_ticket
            == 900000001
        )

    finally:
        session.close()


# ======================================================
# TEST 3
# NON-ALADDIN TRADE IS SKIPPED BY DEFAULT
# ======================================================

def test_mt5_sync_skips_non_aladdin_trade(
    monkeypatch,
):
    session, user = create_test_session()

    try:
        history = fake_aladdin_history()

        history["closed_trades"][0][
            "deal_ticket"
        ] = 900000010

        history["closed_trades"][0][
            "order_ticket"
        ] = 900000011

        history["closed_trades"][0][
            "position_id"
        ] = 900000012

        history["closed_trades"][0][
            "magic"
        ] = 0

        history["closed_trades"][0][
            "comment"
        ] = "Manual trade"

        history["closed_trades"][0][
            "is_aladdin_trade"
        ] = False

        monkeypatch.setattr(
            BrokerService,
            "get_trade_history",
            lambda days=30: history,
        )

        repository = TradeRepository(
            session
        )

        service = JournalService(
            repository
        )

        result = service.sync_mt5_closed_trades(
            user_id=user.id,
            days=30,
        )

        assert result["imported_count"] == 0

        assert result["duplicate_count"] == 0

        assert result["skipped_count"] == 1

        trades = repository.get_user_trades(
            user.id
        )

        assert len(trades) == 0

    finally:
        session.close()