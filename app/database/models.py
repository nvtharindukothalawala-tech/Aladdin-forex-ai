"""
models.py

Database table models for Aladdin.

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

    Supports:
    - Existing Aladdin journal records
    - MT5 synchronized closed trades
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
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(
            timezone.utc
        ),
    )

    # ==================================================
    # JOURNAL SOURCE
    # ==================================================

    source = Column(
        String,
        nullable=True,
        default="ALADDIN",
    )

    # ==================================================
    # MT5 IDENTIFIERS
    # ==================================================

    mt5_deal_ticket = Column(
        Integer,
        nullable=True,
        unique=True,
        index=True,
    )

    mt5_order_ticket = Column(
        Integer,
        nullable=True,
    )

    mt5_position_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    # ==================================================
    # MT5 CLOSED TRADE INFORMATION
    # ==================================================

    close_price = Column(
        Float,
        nullable=True,
    )

    commission = Column(
        Float,
        nullable=True,
        default=0.0,
    )

    swap = Column(
        Float,
        nullable=True,
        default=0.0,
    )

    fee = Column(
        Float,
        nullable=True,
        default=0.0,
    )

    closed_at = Column(
        DateTime,
        nullable=True,
    )

    is_aladdin_trade = Column(
        Integer,
        nullable=True,
        default=0,
    )

    # ==================================================
    # RELATIONSHIP
    # ==================================================

    user = relationship(
        "UserModel",
        back_populates="trades",
    )


class NotificationModel(Base):
    """
    Database model for user notifications.
    """

    __tablename__ = "notifications"

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

    notification_type = Column(
        String,
        nullable=False,
    )

    title = Column(
        String,
        nullable=False,
    )

    message = Column(
        String,
        nullable=False,
    )

    trade_id = Column(
        String,
        nullable=True,
    )

    priority = Column(
        String,
        nullable=False,
        default="INFO",
    )

    is_read = Column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(
            timezone.utc
        ),
    )

    user = relationship(
        "UserModel",
        back_populates="notifications",
    )