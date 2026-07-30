"""
main.py

FastAPI application entry point for
the Aladdin Forex Trading Assistant.

Author: Tharindu Kothalwala
Project: Aladdin
"""


from fastapi import FastAPI

from app.core.config import settings

from app.api.routes import (
    trade_routes,
    analytics_routes,
    risk_routes,
    analysis_routes,
    decision_routes,
)


# ==========================================
# Create FastAPI Application
# ==========================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=(
        "AI-powered Forex Trading Assistant "
        "for trade analysis, risk management, "
        "and decision support."
    ),
)


# ==========================================
# Register API Routes
# ==========================================


# Trade management APIs
app.include_router(
    trade_routes.router
)


# Analytics APIs
app.include_router(
    analytics_routes.router
)


# Risk management APIs
app.include_router(
    risk_routes.router
)


# Market analysis APIs
app.include_router(
    analysis_routes.router
)


# Decision engine APIs
app.include_router(
    decision_routes.router
)


# ==========================================
# Root Endpoint
# ==========================================


@app.get("/")
def home():
    """
    Root API endpoint.

    Returns basic application information.
    """

    return {
        "application": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
    }