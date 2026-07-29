"""
dependencies package

Contains reusable application dependencies.

These dependencies prepare Aladdin Forex AI
for future FastAPI dependency injection.

Author: Tharindu Kothalwala
Project: Aladdin
"""


from app.dependencies.trade_dependencies import (
    get_trade_repository,
    get_trade_service,
)


__all__ = [
    "get_trade_repository",
    "get_trade_service",
]