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
    trading_routes,
    journal_routes,
    performance_routes,
    coaching_routes,
    execution_routes,
)


from app.auth import routes as auth_routes


# ==========================================
# OpenAPI Tag Metadata
# ==========================================

tags_metadata = [

    {
        "name": "Trade",
        "description": (
            "Trade management operations including "
            "creating, viewing, and managing trades."
        ),
    },

    {
        "name": "Analytics",
        "description": (
            "Trading statistics and performance analytics."
        ),
    },

    {
        "name": "Risk",
        "description": (
            "Risk calculation and validation services."
        ),
    },

    {
        "name": "Analysis",
        "description": (
            "Market analysis and intelligence services."
        ),
    },

    {
        "name": "Decision",
        "description": (
            "AI decision engine for trading support."
        ),
    },

    {
        "name": "Trading",
        "description": (
            "Trading workflow and analysis services."
        ),
    },

    {
        "name": "Journal",
        "description": (
            "Trade journaling and AI reasoning records."
        ),
    },

    {
        "name": "Coaching",
        "description": (
            "AI trading coaching and improvement feedback."
        ),
    },

    {
        "name": "Execution",
        "description": (
            "Trade execution workflow services."
        ),
    },

    {
        "name": "Authentication",
        "description": (
            "User registration and authentication APIs."
        ),
    },

]


# ==========================================
# Create FastAPI Application
# ==========================================

app = FastAPI(

    title="Aladdin Forex AI API",

    version="1.1.0",

    description="""

# Aladdin Forex AI

AI-powered multi-agent Forex Trading Assistant API.

## Main Features

- Market intelligence analysis
- Technical analysis
- AI trading decision support
- Risk management
- Trade planning
- Execution workflow
- Trade journaling
- AI coaching
- Performance analytics

## Purpose

Aladdin helps traders make structured and
data-driven decisions.

This system is an assistant tool.
It does not guarantee trading profits
and is not financial advice.

""",

    openapi_tags=tags_metadata,

    contact={
        "name": "Tharindu Kothalwala",
        "url": (
            "https://github.com/"
            "nvtharindukothalawala-tech"
        ),
    },

    license_info={
        "name": "MIT License",
    },

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


# Trading APIs

app.include_router(
    trading_routes.router
)


# Journal APIs

app.include_router(
    journal_routes.router
)


# Performance APIs

app.include_router(
    performance_routes.router
)


# Coaching APIs

app.include_router(
    coaching_routes.router
)


# Execution APIs

app.include_router(
    execution_routes.router
)


# Authentication APIs

app.include_router(
    auth_routes.router
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

        "version": "1.1.0",

        "status": "running",

        "message": (
            "Aladdin Forex AI API is running"
        ),

    }