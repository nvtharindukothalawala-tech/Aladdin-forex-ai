"""
execution_schema.py

API schemas for trade execution.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel, ConfigDict


class ExecutionRequestSchema(BaseModel):
    """
    Input schema for execution request.
    """

    user_id: int

    symbol: str

    direction: str

    volume: float


class ExecutionResponseSchema(BaseModel):
    """
    Response schema after execution.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    symbol: str

    direction: str

    volume: float

    status: str

    broker_order_id: str | None


class ExecutionHistoryResponseSchema(BaseModel):
    """
    Response schema for execution history.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    symbol: str

    direction: str

    volume: float

    status: str

    broker_order_id: str | None


class ExecutionStatisticsResponseSchema(BaseModel):
    """
    Response schema for execution statistics.
    """

    total_executions: int

    successful_executions: int

    failed_executions: int

    success_rate: float