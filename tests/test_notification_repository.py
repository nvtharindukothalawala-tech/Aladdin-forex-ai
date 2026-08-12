"""
test_notification_repository.py

Tests notification database repository.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from app.database.connection import SessionLocal

from app.database.notification_repository import (
    NotificationRepository,
)


def test_create_notification():
    """
    Verify that a notification can be saved
    to the database.
    """

    session = SessionLocal()

    repository = NotificationRepository(session)

    notification = repository.create_notification(
        user_id=1,
        notification_type="TRADE_OPENED",
        title="Trade Opened",
        message="EUR/USD BUY trade has been opened.",
        trade_id="TRD0001",
        priority="SUCCESS",
    )

    assert notification.id is not None
    assert notification.user_id == 1
    assert notification.notification_type == "TRADE_OPENED"
    assert notification.title == "Trade Opened"
    assert notification.trade_id == "TRD0001"
    assert notification.is_read == 0

    session.close()


def test_get_user_notifications():
    """
    Verify that notifications can be retrieved
    for a specific user.
    """

    session = SessionLocal()

    repository = NotificationRepository(session)

    repository.create_notification(
        user_id=1,
        notification_type="TRADE_OPENED",
        title="Trade Opened",
        message="EUR/USD BUY trade has been opened.",
        trade_id="TRD0002",
        priority="SUCCESS",
    )

    notifications = repository.get_user_notifications(
        user_id=1
    )

    assert isinstance(notifications, list)
    assert len(notifications) >= 1

    session.close()


def test_get_unread_notifications():
    """
    Verify that unread notifications can be retrieved.
    """

    session = SessionLocal()

    repository = NotificationRepository(session)

    notification = repository.create_notification(
        user_id=1,
        notification_type="RISK_WARNING",
        title="Risk Warning",
        message="Trade risk is too high.",
        priority="WARNING",
    )

    unread = repository.get_unread_notifications(
        user_id=1
    )

    assert any(
        item.id == notification.id
        for item in unread
    )

    session.close()


def test_mark_notification_as_read():
    """
    Verify that one notification can be marked as read.
    """

    session = SessionLocal()

    repository = NotificationRepository(session)

    notification = repository.create_notification(
        user_id=1,
        notification_type="TRADE_CLOSED",
        title="Trade Closed",
        message="EUR/USD trade has been closed.",
        trade_id="TRD0003",
        priority="INFO",
    )

    updated = repository.mark_as_read(
        notification_id=notification.id,
        user_id=1,
    )

    assert updated is not None
    assert updated.is_read == 1

    session.close()


def test_mark_all_notifications_as_read():
    """
    Verify that all unread notifications can be marked
    as read for a user.
    """

    session = SessionLocal()

    repository = NotificationRepository(session)

    repository.create_notification(
        user_id=1,
        notification_type="TRADE_OPENED",
        title="Trade Opened",
        message="Trade opened.",
        priority="SUCCESS",
    )

    repository.create_notification(
        user_id=1,
        notification_type="RISK_WARNING",
        title="Risk Warning",
        message="Risk warning.",
        priority="WARNING",
    )

    count = repository.mark_all_as_read(
        user_id=1
    )

    assert count >= 2

    unread = repository.get_unread_notifications(
        user_id=1
    )

    assert len(unread) == 0

    session.close()