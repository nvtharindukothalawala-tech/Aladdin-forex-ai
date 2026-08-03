# Aladdin Forex AI Deployment Guide

## Overview

This document explains how to set up, run, and deploy the **Aladdin Forex AI** system.

Aladdin supports multiple deployment environments:

- Local development environment
- Docker-based development environment
- Production Docker environment with PostgreSQL

The system is designed as an AI-powered Forex Trading Assistant and not as a guaranteed profit trading bot.

---

# 1. Local Development Setup

## Requirements

Before running Aladdin locally, install:

- Python 3.14+
- Git
- Virtual Environment support

---

## Create Virtual Environment

Create a Python virtual environment:

```bash
python -m venv .venv

2. Environment Configuration

Create a .env file in the project root directory.

Example:

APP_NAME=Aladdin Forex AI
APP_VERSION=1.1.0
ENVIRONMENT=development

LOG_LEVEL=INFO

DATA_FOLDER=data
TRADES_FILE=data/trades.json

DEFAULT_CURRENCY=USD
DEFAULT_RISK_PERCENT=1.0

DATABASE_URL=sqlite:///./aladdin.db
Database Configuration

During local development, Aladdin uses:

SQLite

Database file:

aladdin.db

For production deployment, PostgreSQL can be configured using:

DATABASE_URL=postgresql://username:password@host:5432/database
3. Running the Application Locally

Start the FastAPI application:

uvicorn app.api.main:app --reload

The API will start at:

http://localhost:8000
API Documentation

Swagger UI:

http://localhost:8000/docs

OpenAPI specification:

http://localhost:8000/openapi.json
Health Check

Health endpoint:

GET /health

Example response:

{
  "status": "healthy",
  "service": "Aladdin Forex AI",
  "version": "1.1.0"
}
4. Docker Development Deployment

Aladdin provides Docker support for consistent development environments.

Build and Run

Start the development container:

docker compose up --build

The API will be available at:

http://localhost:8000
Stop Docker Environment

Stop containers:

docker compose down
5. Production Docker Deployment

The production environment uses:

FastAPI application container
PostgreSQL database container
Environment-based configuration
Docker health monitoring

Production configuration file:

docker-compose.prod.yml
Start Production Environment

Build and start production services:

docker compose -f docker-compose.prod.yml up --build

This starts:

aladdin-forex-ai-prod
        |
        |
        ↓
PostgreSQL 16 Database
Stop Production Environment

Stop production containers:

docker compose -f docker-compose.prod.yml down
6. Production Database Configuration

Production uses PostgreSQL.

Database connection format:

postgresql://username:password@host:5432/database

Example:

DATABASE_URL=postgresql://aladdin_user:aladdin_password@postgres:5432/aladdin_db

The PostgreSQL container provides:

Persistent database storage
Health monitoring
Internal Docker networking
7. Docker Health Monitoring

The application includes Docker health checks.

API health check:

GET /health

Docker verifies:

FastAPI container → Healthy
PostgreSQL container → Healthy

Check running containers:

docker ps

Example:

aladdin-forex-ai-prod       Up (healthy)
aladdin-postgres-prod       Up (healthy)
8. CI/CD Pipeline

Aladdin uses GitHub Actions for continuous integration.

The CI pipeline performs:

Repository checkout
Python environment setup
Dependency installation
Automated testing
Docker image build verification

Workflow file:

.github/workflows/ci.yml
9. Production Deployment Flow

The production workflow:

Developer
    |
    ↓
GitHub Repository
    |
    ↓
GitHub Actions CI
    |
    ↓
Docker Image Build
    |
    ↓
Production Deployment
    |
    ↓
FastAPI + PostgreSQL
10. Future Cloud Deployment

The current architecture is prepared for cloud deployment using:

Docker hosting platforms
Managed PostgreSQL databases
Secure environment variables
Automated CI/CD deployment

Future improvements include:

Cloud database migration
Monitoring and logging services
Automated deployment pipelines
Production security configuration
Summary

Aladdin Forex AI currently supports:

✅ Local Python development
✅ SQLite development database
✅ Docker deployment
✅ PostgreSQL production environment
✅ Health monitoring
✅ CI/CD validation

The project architecture is designed for future scalable deployment.

