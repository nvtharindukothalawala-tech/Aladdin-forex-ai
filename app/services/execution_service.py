"""
execution_service.py

Business logic for trade execution lifecycle.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.execution.execution_manager import (
    ExecutionManager,
)


class ExecutionService:
    """
    Handles complete execution workflow.
    """

    def __init__(
        self,
        repository,
    ):

        self.repository = repository

    def execute_trade(
        self,
        user_id: int,
        execution_request,
    ):
        """
        Execute approved trade
        and store execution history.
        """

        result = ExecutionManager.execute_with_mt5(execution_request)

        status = "EXECUTED" if result.success else "FAILED"

        execution = self.repository.save_execution(
            user_id=user_id,
            symbol=execution_request.symbol,
            direction=execution_request.order_type,
            volume=execution_request.volume,
            status=status,
            broker_order_id=result.order_id,
        )

        return execution
