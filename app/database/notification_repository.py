"""
notification_repository.py

Database operations for Aladdin notifications.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from app.database.models import NotificationModel


class NotificationRepository:
    """
    Handles notification database operations.
    """

    def __init__(self, session):
        self.session = session

    # ==========================================
    # Create Notification
    # ==========================================

    def create_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        trade_id: str | None = None,
        priority: str = "INFO",
    ):
        """
        Create and save a notification.
        """

        notification = NotificationModel(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            trade_id=trade_id,
            priority=priority,
            is_read=0,
        )

        self.session.add(notification)

        self.session.commit()

        self.session.refresh(notification)

        return notification

    # ==========================================
    # Get All Notifications
    # ==========================================

    def get_user_notifications(
        self,
        user_id: int,
    ):
        """
        Return all notifications belonging to a user.
        """

        return (
            self.session.query(NotificationModel)
            .filter(
                NotificationModel.user_id == user_id
            )
            .order_by(
                NotificationModel.created_at.desc()
            )
            .all()
        )

    # ==========================================
    # Get Unread Notifications
    # ==========================================

    def get_unread_notifications(
        self,
        user_id: int,
    ):
        """
        Return unread notifications for a user.
        """

        return (
            self.session.query(NotificationModel)
            .filter(
                NotificationModel.user_id == user_id,
                NotificationModel.is_read == 0,
            )
            .order_by(
                NotificationModel.created_at.desc()
            )
            .all()
        )

    # ==========================================
    # Count Unread Notifications
    # ==========================================

    def count_unread_notifications(
        self,
        user_id: int,
    ):
        """
        Return the number of unread notifications
        belonging to a user.
        """

        return (
            self.session.query(NotificationModel)
            .filter(
                NotificationModel.user_id == user_id,
                NotificationModel.is_read == 0,
            )
            .count()
        )

    # ==========================================
    # Mark One Notification As Read
    # ==========================================

    def mark_as_read(
        self,
        notification_id: int,
        user_id: int,
    ):
        """
        Mark one notification as read.
        """

        notification = (
            self.session.query(NotificationModel)
            .filter(
                NotificationModel.id == notification_id,
                NotificationModel.user_id == user_id,
            )
            .first()
        )

        if notification is None:
            return None

        notification.is_read = 1

        self.session.commit()

        self.session.refresh(notification)

        return notification

    # ==========================================
    # Mark All Notifications As Read
    # ==========================================

    def mark_all_as_read(
        self,
        user_id: int,
    ):
        """
        Mark all user notifications as read.
        """

        notifications = (
            self.session.query(NotificationModel)
            .filter(
                NotificationModel.user_id == user_id,
                NotificationModel.is_read == 0,
            )
            .all()
        )

        for notification in notifications:
            notification.is_read = 1

        self.session.commit()

        return len(notifications)