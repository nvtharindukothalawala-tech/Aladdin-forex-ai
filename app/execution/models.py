"""
models.py

Database models for trade execution history.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from datetime import datetime, timezone


from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
)


from app.database.models import Base


class ExecutionModel(Base):
    """
    Stores execution history.
    """

    __tablename__ = "execution_orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        nullable=False,
    )

    symbol = Column(
        String,
        nullable=False,
    )

    direction = Column(
        String,
        nullable=False,
    )

    volume = Column(
        Float,
        nullable=False,
    )

    status = Column(
        String,
        nullable=False,
    )

    broker_order_id = Column(
        String,
        nullable=True,
    )

    execution_message = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )