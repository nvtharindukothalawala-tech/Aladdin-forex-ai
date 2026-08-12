"""
notification_service.py

Business logic for Aladdin notifications.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from app.core.logger import get_logger


class NotificationService:
    """
    Manage user notifications.

    This service uses NotificationRepository for
    database operations.
    """

    logger = get_logger(__name__)

    def __init__(self, repository):
        """
        Create the notification service.

        Args:
            repository:
                Repository used for notification storage.
        """

        self.repository = repository

    # ==========================================
    # Create Notification
    # ==========================================

    def create_notification(
        self,
        user_id,
        notification_type,
        title,
        message,
        trade_id=None,
        priority="INFO",
    ):
        """
        Create a new notification for a user.
        """

        notification = (
            self.repository.create_notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                trade_id=trade_id,
                priority=priority,
            )
        )

        self.logger.info(
            "Notification created for user %s: %s",
            user_id,
            notification_type,
        )

        return notification

    # ==========================================
    # Get Notifications
    # ==========================================

    def get_user_notifications(
        self,
        user_id,
    ):
        """
        Return all notifications belonging
        to a user.
        """

        return (
            self.repository.get_user_notifications(
                user_id
            )
        )

    # ==========================================
    # Get Unread Notifications
    # ==========================================

    def get_unread_notifications(
        self,
        user_id,
    ):
        """
        Return unread notifications belonging
        to a user.
        """

        return (
            self.repository.get_unread_notifications(
                user_id
            )
        )

    # ==========================================
    # Count Unread Notifications
    # ==========================================

    def count_unread_notifications(
        self,
        user_id,
    ):
        """
        Return the number of unread notifications
        belonging to a user.
        """

        return (
            self.repository.count_unread_notifications(
                user_id
            )
        )

    # ==========================================
    # Mark As Read
    # ==========================================

    def mark_as_read(
        self,
        notification_id,
        user_id,
    ):
        """
        Mark one notification as read.
        """

        notification = (
            self.repository.mark_as_read(
                notification_id=notification_id,
                user_id=user_id,
            )
        )

        if notification is not None:

            self.logger.info(
                "Notification marked as read: %s",
                notification_id,
            )

        return notification

    # ==========================================
    # Mark All As Read
    # ==========================================

    def mark_all_as_read(
        self,
        user_id,
    ):
        """
        Mark all notifications for a user as read.
        """

        count = (
            self.repository.mark_all_as_read(
                user_id
            )
        )

        self.logger.info(
            "Marked %s notifications as read for user %s.",
            count,
            user_id,
        )

        return count