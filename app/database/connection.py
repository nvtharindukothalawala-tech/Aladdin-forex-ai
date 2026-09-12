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
from sqlalchemy import create_engine
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
)


# ======================================================
# DATABASE TABLE INITIALIZATION
# ======================================================

def create_database_tables():
    """
    Create all registered database tables.

    Existing tables are not deleted.
    SQLAlchemy only creates tables that are missing.
    """

    Base.metadata.create_all(
        bind=engine,
    )


# Automatically create missing tables when this
# database module is loaded.
#
# This allows fresh environments such as GitHub CI
# to create execution_orders and the other tables
# before services and tests use them.

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