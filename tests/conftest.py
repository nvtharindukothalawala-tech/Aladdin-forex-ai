"""
conftest.py

Test environment and database configuration.

Author: Tharindu Kothalwala
Project: Aladdin
"""

import os


# ============================================================
# TEST EXECUTION ENVIRONMENT
# ============================================================
# IMPORTANT:
# These must be set BEFORE importing application modules.
#
# Tests use MOCK mode so they never send an order to the
# connected MT5 DEMO account.
#
# Your normal application can still use:
# ALADDIN_MT5_MODE=DEMO
# ALADDIN_ENABLE_DEMO_EXECUTION=true
# from the project .env file.
# ============================================================

os.environ["ALADDIN_MT5_MODE"] = "MOCK"
os.environ["ALADDIN_ENABLE_DEMO_EXECUTION"] = "false"


# ============================================================
# APPLICATION IMPORTS
# ============================================================

from app.database.connection import engine
from app.database.models import Base

# Import models so SQLAlchemy knows all tables.
from app.database import models
from app.auth import models as auth_models


# ============================================================
# PYTEST CONFIGURATION
# ============================================================

def pytest_configure():
    """
    Create database tables before tests.
    """

    Base.metadata.create_all(
        bind=engine
    )