"""
routes package

Contains FastAPI route modules.

Author: Tharindu Kothalwala
Project: Aladdin
"""


from app.api.routes import (
    trade_routes,
    analytics_routes,
    risk_routes,
    analysis_routes,
    decision_routes,
    trading_routes,
    journal_routes,
    performance_routes,
    coaching_routes,
)


__all__ = [
    "trade_routes",
    "analytics_routes",
    "risk_routes",
    "analysis_routes",
    "decision_routes",
    "trading_routes",
    "journal_routes",
    "performance_routes",
    "coaching_routes",
]