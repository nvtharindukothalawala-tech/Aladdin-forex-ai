"""
notification_routes.py

API endpoints for user notifications.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_database,
    get_current_user,
)

from app.auth.models import UserModel

from app.database.notification_repository import (
    NotificationRepository,
)

from app.services.notification_service import (
    NotificationService,
)

from app.schemas.notification_schema import (
    NotificationResponseSchema,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


# ==========================================
# Get All Notifications
# ==========================================

@router.get(
    "",
    response_model=list[NotificationResponseSchema],
)
def get_notifications(
    database: Session = Depends(get_database),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Return all notifications for the
    authenticated user.
    """

    repository = NotificationRepository(
        database
    )

    service = NotificationService(
        repository
    )

    return service.get_user_notifications(
        current_user.id
    )


# ==========================================
# Get Unread Notifications
# ==========================================

@router.get(
    "/unread",
    response_model=list[NotificationResponseSchema],
)
def get_unread_notifications(
    database: Session = Depends(get_database),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Return unread notifications for the
    authenticated user.
    """

    repository = NotificationRepository(
        database
    )

    service = NotificationService(
        repository
    )

    return service.get_unread_notifications(
        current_user.id
    )


# ==========================================
# Count Unread Notifications
# ==========================================

@router.get(
    "/unread/count",
)
def get_unread_notification_count(
    database: Session = Depends(get_database),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Return the number of unread notifications
    for the authenticated user.
    """

    repository = NotificationRepository(
        database
    )

    service = NotificationService(
        repository
    )

    count = service.count_unread_notifications(
        current_user.id
    )

    return {
        "unread_count": count
    }


# ==========================================
# Mark One Notification As Read
# ==========================================

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponseSchema,
)
def mark_notification_as_read(
    notification_id: int,
    database: Session = Depends(get_database),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Mark one notification as read.
    """

    repository = NotificationRepository(
        database
    )

    service = NotificationService(
        repository
    )

    return service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )


# ==========================================
# Mark All Notifications As Read
# ==========================================

@router.patch(
    "/read-all",
)
def mark_all_notifications_as_read(
    database: Session = Depends(get_database),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Mark all notifications for the
    authenticated user as read.
    """

    repository = NotificationRepository(
        database
    )

    service = NotificationService(
        repository
    )

    count = service.mark_all_as_read(
        current_user.id
    )

    return {
        "message": "Notifications marked as read.",
        "count": count,
    }