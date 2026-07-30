"""
conftest.py

Test database configuration.

Author: Tharindu Kothalwala
Project: Aladdin
"""


from app.database.connection import engine

from app.database.models import Base

# Import models so SQLAlchemy knows tables

from app.database import models

from app.auth import models as auth_models



def pytest_configure():

    """
    Create database tables before tests.
    """

    Base.metadata.create_all(
        bind=engine
    )