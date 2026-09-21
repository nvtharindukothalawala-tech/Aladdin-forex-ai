"""
connection.py

Database connection setup.

Supports:
- SQLite for local development
- PostgreSQL for production deployment

Author: Tharindu Kothalawala
Project: Aladdin
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker


# ======================================================
# ENVIRONMENT
# ======================================================

load_dotenv()


DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or "sqlite:///./aladdin.db"
)


# ======================================================
# DATABASE ENGINE
# ======================================================

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)


# ======================================================
# DATABASE SESSION
# ======================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ======================================================
# ORM MODEL REGISTRATION
# ======================================================
#
# All SQLAlchemy models that use the shared Base
# must be imported before Base.metadata.create_all().
#
# This ensures SQLAlchemy knows about:
# - users
# - trades
# - notifications
# - execution_orders
# - execution_safety_audits
#
# This is especially important for fresh databases
# such as GitHub Actions CI.
# ======================================================

from app.database.models import (  # noqa: E402, F401
    Base,
    TradeModel,
    NotificationModel,
)

from app.auth.models import (  # noqa: E402, F401
    UserModel,
)

from app.execution.models import (  # noqa: E402, F401
    ExecutionModel,
    ExecutionSafetyAuditModel,
)


# ======================================================
# EXECUTION IDEMPOTENCY SCHEMA COMPATIBILITY
# ======================================================

def ensure_execution_idempotency_schema():
    """
    Upgrade an existing execution_orders table so it supports
    execution idempotency.

    Fresh databases already receive these fields through the
    SQLAlchemy ExecutionModel. Existing databases created before
    Phase 7 require the new nullable columns to be added manually
    because Base.metadata.create_all() does not modify existing
    tables.

    The unique index is scoped by:
        user_id + idempotency_key

    This allows:
    - different users to use the same idempotency key,
    - legacy rows to keep NULL idempotency keys,
    - duplicate execution keys for one user to be rejected by
      the database.
    """

    inspector = inspect(engine)

    if "execution_orders" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("execution_orders")
    }

    with engine.begin() as connection:
        if "idempotency_key" not in existing_columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE execution_orders
                    ADD COLUMN idempotency_key VARCHAR(128)
                    """
                )
            )

        if "request_fingerprint" not in existing_columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE execution_orders
                    ADD COLUMN request_fingerprint VARCHAR(64)
                    """
                )
            )

    # Re-inspect after any ALTER TABLE statements.
    inspector = inspect(engine)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes("execution_orders")
        if index.get("name")
    }

    index_name = "ux_execution_orders_user_idempotency_key"

    if index_name not in existing_indexes:
        with engine.begin() as connection:
            connection.execute(
                text(
                    f"""
                    CREATE UNIQUE INDEX {index_name}
                    ON execution_orders (user_id, idempotency_key)
                    """
                )
            )


# ======================================================
# DATABASE TABLE INITIALIZATION
# ======================================================

def create_database_tables():
    """
    Create all registered database tables.

    Existing tables are not deleted.

    Fresh databases receive the complete current schema through
    SQLAlchemy. Existing databases are then checked for backward-
    compatible execution idempotency fields.

    The execution_safety_audits table is a new table, so
    Base.metadata.create_all() creates it automatically when
    missing. No ALTER TABLE compatibility step is required.
    """

    Base.metadata.create_all(
        bind=engine,
    )

    ensure_execution_idempotency_schema()


# Automatically create missing tables when this
# database module is loaded.
#
# This allows fresh environments such as GitHub CI
# to create execution_orders, execution_safety_audits,
# and the other registered tables before services and
# tests use them.
#
# Existing local databases are also upgraded with the
# Phase 7 execution idempotency fields when required.

create_database_tables()


# ======================================================
# DATABASE DEPENDENCY
# ======================================================

def get_db():
    """
    Provide a database session.

    Used as a FastAPI dependency.

    The session is always closed after the request
    finishes.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
