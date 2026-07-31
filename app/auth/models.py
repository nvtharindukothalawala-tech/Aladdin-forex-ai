"""
models.py

Authentication database models.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from datetime import datetime


from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)


from sqlalchemy.orm import relationship


from app.database.models import Base


class UserModel(Base):
    """
    User database table.
    """

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    username = Column(
        String,
        unique=True,
        nullable=False,
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
    )

    password_hash = Column(
        String,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    # Relationship with TradeModel
    trades = relationship(
        "TradeModel",
        back_populates="user",
    )
