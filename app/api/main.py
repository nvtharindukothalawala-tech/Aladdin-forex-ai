"""
main.py

FastAPI application entry point for
the Aladdin Forex Trading Assistant.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    notification_routes,
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
        "name": "Notifications",
        "description": (
            "User notifications and trade status alerts."
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
        "name": "Tharindu Kothalawala",
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
# CORS
# ==========================================
#
# Allows the Next.js frontend running on
# localhost:3000 to communicate with
# the FastAPI backend.
#
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# Notification APIs

app.include_router(
    notification_routes.router
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


# ==========================================
# Health Check Endpoint
# ==========================================

@app.get("/health")
def health_check():
    """
    Health check endpoint.

    Used by Docker, monitoring tools,
    and deployment platforms.
    """

    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.1.0",
    }