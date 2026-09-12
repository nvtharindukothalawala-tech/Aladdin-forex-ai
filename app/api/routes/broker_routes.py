"""
broker_routes.py

Read-only MT5 broker monitoring endpoints.

Provides:
- Broker status
- Account information
- Open positions
- Closed trade history

These endpoints do not create,
modify, or close trades.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from app.services.broker_service import (
    BrokerService,
)

router = APIRouter(
    prefix="/broker",
    tags=["Broker Monitoring"],
)


@router.get("/status")
def get_broker_status():
    """
    Return combined MT5 broker status.

    Includes:
    - Account information
    - Open positions
    """

    try:
        return BrokerService.get_broker_status()

    except (
        ConnectionError,
        PermissionError,
        ValueError,
    ) as error:

        raise HTTPException(
            status_code=503,
            detail=str(error),
        )


@router.get("/account")
def get_account_information():
    """
    Return MT5 account information.

    Read-only endpoint.
    """

    try:
        return BrokerService.get_account_info()

    except (
        ConnectionError,
        PermissionError,
        ValueError,
    ) as error:

        raise HTTPException(
            status_code=503,
            detail=str(error),
        )


@router.get("/positions")
def get_open_positions():
    """
    Return currently open MT5 positions.

    Read-only endpoint.
    """

    try:
        return BrokerService.get_open_positions()

    except (
        ConnectionError,
        PermissionError,
        ValueError,
    ) as error:

        raise HTTPException(
            status_code=503,
            detail=str(error),
        )


@router.get("/history")
def get_trade_history(
    days: int = Query(
        default=30,
        ge=1,
        le=3650,
        description=(
            "Number of days of MT5 "
            "closed trade history to load."
        ),
    ),
):
    """
    Return closed MT5 trade history.

    Default:
        Last 30 days.

    Maximum:
        3650 days.

    This endpoint is completely read-only.
    """

    try:
        return BrokerService.get_trade_history(
            days=days,
        )

    except (
        ConnectionError,
        PermissionError,
        ValueError,
    ) as error:

        raise HTTPException(
            status_code=503,
            detail=str(error),
        )