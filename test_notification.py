from app.database.connection import SessionLocal
from app.database.notification_repository import NotificationRepository
from app.services.notification_service import NotificationService
from app.auth.models import UserModel


# Create database session
session = SessionLocal()

try:
    # Find the test user
    user = (
        session.query(UserModel)
        .filter(UserModel.username == "tharindu")
        .first()
    )

    if user is None:
        print("ERROR: User 'tharindu' was not found.")
        print("Please register the user first.")
    else:
        # Create repository
        repository = NotificationRepository(session)

        # Create service
        service = NotificationService(repository)

        # Create test notification
        notification = service.create_notification(
            user_id=user.id,
            notification_type="SYSTEM",
            title="Welcome to Aladdin",
            message="This is a test notification from the Aladdin notification system.",
            trade_id=None,
            priority="INFO",
        )

        print()
        print("========================================")
        print("TEST NOTIFICATION CREATED")
        print("========================================")
        print(f"Notification ID : {notification.id}")
        print(f"User ID         : {notification.user_id}")
        print(f"Title           : {notification.title}")
        print(f"Message         : {notification.message}")
        print(f"Priority        : {notification.priority}")
        print(f"Read status     : {notification.is_read}")
        print("========================================")

finally:
    session.close()