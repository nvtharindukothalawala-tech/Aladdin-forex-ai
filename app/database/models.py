"""
models.py

Database table models for Aladdin.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from datetime import datetime, timezone


from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
)


from sqlalchemy.orm import (
    declarative_base,
    relationship,
)


Base = declarative_base()


class TradeModel(Base):
    """
    Database model for completed trades.
    """

    __tablename__ = "trades"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
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

    result = Column(
        String,
        nullable=False,
    )

    profit_loss = Column(
        Float,
        nullable=False,
    )

    risk_reward = Column(
        Float,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationship with UserModel
    user = relationship(
        "UserModel",
        back_populates="trades",
    )