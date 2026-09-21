"""
models.py

Database models for trade execution history and
deterministic execution-safety audit snapshots.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)

from app.database.models import Base


class ExecutionModel(Base):
    """
    Stores execution history.

    Idempotency fields are nullable so legacy execution records and
    backward-compatible API requests can continue to work.

    When an idempotency key is supplied, the combination of
    user_id + idempotency_key must be unique. The request fingerprint
    is used to detect attempts to reuse the same key for a different
    execution request.
    """

    __tablename__ = "execution_orders"

    __table_args__ = (
        Index(
            "ux_execution_orders_user_idempotency_key",
            "user_id",
            "idempotency_key",
            unique=True,
        ),
    )

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

    idempotency_key = Column(
        String(128),
        nullable=True,
    )

    request_fingerprint = Column(
        String(64),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(
            timezone.utc
        ),
    )


class ExecutionSafetyAuditModel(Base):
    """
    Immutable snapshot of the deterministic safety
    decision that authorized an execution.

    One execution can have at most one safety audit
    snapshot.
    """

    __tablename__ = "execution_safety_audits"

    __table_args__ = (
        Index(
            "ux_execution_safety_audits_execution_id",
            "execution_id",
            unique=True,
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    execution_id = Column(
        Integer,
        ForeignKey("execution_orders.id"),
        nullable=False,
    )

    user_id = Column(
        Integer,
        nullable=False,
    )

    safety_status = Column(
        String,
        nullable=False,
    )

    safety_engine = Column(
        String,
        nullable=False,
    )

    execution_mode = Column(
        String,
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

    entry_price = Column(
        Float,
        nullable=True,
    )

    stop_loss = Column(
        Float,
        nullable=True,
    )

    take_profit = Column(
        Float,
        nullable=True,
    )

    checks_json = Column(
        Text,
        nullable=False,
    )

    reasons_json = Column(
        Text,
        nullable=False,
    )

    limits_json = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(
            timezone.utc
        ),
        nullable=False,
    )
