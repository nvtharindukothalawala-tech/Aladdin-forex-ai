"""
connection.py

Database connection setup.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./aladdin.db"


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
