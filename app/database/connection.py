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
# SQLAlchemy relationships such as:
#
# relationship("UserModel")
#
# use class names stored in the SQLAlchemy model
# registry.
#
# Therefore UserModel must be imported before
# SQLAlchemy configures all model relationships.
#
# This import is intentionally placed after the
# database engine/session configuration.
# ======================================================

# ORM model registration
#
# Import related models so SQLAlchemy can resolve
# relationship names such as "TradeModel" and
# "NotificationModel".

from app.database.models import (  # noqa: E402, F401
    TradeModel,
    NotificationModel,
)

from app.auth.models import (  # noqa: E402, F401
    UserModel,
)