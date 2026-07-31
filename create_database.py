"""
create_database.py

Creates Aladdin database tables.

Author: Tharindu Kothalwala
Project: Aladdin
"""


from app.database.connection import engine

from app.database.models import Base

# Import models so SQLAlchemy registers all tables
from app.auth.models import UserModel
from app.database.models import TradeModel



Base.metadata.create_all(
    bind=engine
)


print(
    "Database tables created successfully."
)