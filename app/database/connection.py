"""
connection.py

Database connection setup.

Supports:
- SQLite for local development
- PostgreSQL for production deployment

Author: Tharindu Kothalwala
Project: Aladdin
"""

import os

from dotenv import load_dotenv

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker


# Load environment variables
load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL"
) or "sqlite:///./aladdin.db"


# SQLite requires this option
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)