"""
execution_service.py

Business logic for trade execution lifecycle.

Author: Tharindu Kothalawala
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

        try:

            result = (
                ExecutionManager.execute_with_mt5(
                    execution_request
                )
            )

            status = (
                "EXECUTED"
                if result.success
                else "FAILED"
            )

            order_id = (
                result.order_id
                if result.success
                else None
            )

            execution_message = result.message

        except Exception as error:

            status = "FAILED"

            order_id = None

            execution_message = str(error)

        execution = self.repository.save_execution(
            user_id=user_id,
            symbol=execution_request.symbol,
            direction=execution_request.order_type,
            volume=execution_request.volume,
            status=status,
            broker_order_id=order_id,
            execution_message=execution_message,
        )

        return execution