# Contributing to Aladdin Forex AI

Thank you for your interest in contributing to Aladdin Forex AI.

This document explains the development process and project guidelines.

---

# Development Setup

## 1. Clone the repository

```bash
git clone <repository-url>

# Contributing to Aladdin Forex AI

Thank you for your interest in contributing to Aladdin Forex AI.

This document explains the development process, coding standards, and project guidelines for contributors.

---

# Development Setup

Follow these steps to prepare your local development environment.

---

## 1. Clone the Repository

Clone the project from GitHub:

```bash
git clone <repository-url>

Move into the project folder:

cd Aladdin-forex-ai
2. Create Virtual Environment

Create a Python virtual environment:

python -m venv .venv

The virtual environment keeps project dependencies separate from the system Python installation.

3. Activate Virtual Environment

Windows:

.venv\Scripts\activate

After activation, the terminal should show:

(.venv)
4. Install Dependencies

Install all required project packages:

pip install -r requirements.txt

This installs the required libraries used by Aladdin Forex AI.

Running the Application

Start the Aladdin Forex AI application:

python -m app.main

The application will initialize:

Account management
Trade services
Repository system
Logging system

Example:

ALADDIN FOREX AI
Trading Assistant System

Accounts:
ACC001 | Balance: 5000 USD | Leverage: 100

Trades Loaded: 4
Running Tests

Aladdin Forex AI uses Pytest for automated testing.

Run all tests:

pytest

The test suite checks:

Account creation
Account validation
Deposit and withdrawal operations
Trade creation
Trade closing
Profit calculation
Risk calculations
Repository storage
Trade analytics
Service operations
Custom exceptions

Current test status:

62 passed

All tests should pass before submitting changes.

Code Style Guidelines

The project follows clean Python development practices.

Contributors should:

Use meaningful variable names
Write simple and readable code
Keep functions focused on one responsibility
Add comments for important logic
Maintain the existing project structure
Avoid unnecessary complexity
Code Formatting

Aladdin uses Black for automatic Python code formatting.

Run:

black .

This keeps the code style consistent throughout the project.

Commit Message Guidelines

Use clear and meaningful commit messages.

Good Examples:
Add trade validation system
Fix risk calculation error
Update project documentation
Add logging support
Avoid:
update
changes
fix stuff

Commit messages should explain what was changed.

Development Workflow

Follow this workflow when adding new features.

1. Create a new branch

Example:

git checkout -b feature-name
2. Make Changes

Implement the required feature or fix.

Make sure changes follow the existing architecture.

3. Run Tests

Before committing:

pytest

Make sure all tests pass.

4. Format Code

Run:

black .
5. Commit Changes

Example:

git add .
git commit -m "Add new feature"
6. Push Changes
git push
Project Architecture Guidelines

Aladdin follows a layered architecture.

New features should be added to the correct layer.

app/

├── core/
│   Configuration, logging, and exceptions
│
├── models/
│   Business objects and data models
│
├── services/
│   Application business logic
│
├── repositories/
│   Data storage operations
│
└── risk/
    Risk calculation logic
Development Principles

When improving Aladdin:

Keep existing features working.
Add tests for new functionality.
Update documentation when required.
Maintain clean architecture.
Write understandable and maintainable code.
Testing Requirements

Before submitting changes:

Run the test suite.
pytest
Confirm all tests pass.
Check that new features have proper test coverage.
Project Goal

Aladdin Forex AI is an AI-powered Forex Trading Assistant.

The project focuses on:

Forex trade management
Risk management
Trading analytics
Decision support
Learning from trading history

The system is designed to help traders make better decisions.

It does not guarantee profits and does not replace professional trading decisions.

Author

Tharindu Kothalwala

Project:

Aladdin Forex AI


After saving this file:

Run:

```powershell
git status