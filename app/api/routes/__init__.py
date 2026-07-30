"""
routes package

Contains FastAPI route modules.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.api.routes import trade_routes
from app.api.routes import analytics_routes

__all__ = [
    "trade_routes",
    "analytics_routes",
]
