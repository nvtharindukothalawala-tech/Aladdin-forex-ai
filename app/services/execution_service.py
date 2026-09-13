"""
execution_service.py

Business logic for trade execution lifecycle.

Author: Tharindu Kothalawala
Project: Aladdin
"""

import os

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

    @staticmethod
    def _get_execution_mode() -> str:
        """
        Return the currently configured
        MT5 execution mode.

        Supported modes:
        - MOCK
        - DEMO
        """

        return os.getenv(
            "ALADDIN_MT5_MODE",
            "MOCK",
        ).strip().upper()

    @staticmethod
    def _is_demo_execution_enabled() -> bool:
        """
        Check whether real MT5 DEMO order
        sending is enabled.

        The safety switch is enabled only
        when the environment variable is
        explicitly set to 'true'.
        """

        return (
            os.getenv(
                "ALADDIN_ENABLE_DEMO_EXECUTION",
                "false",
            )
            .strip()
            .lower()
            == "true"
        )

    def execute_trade(
        self,
        user_id: int,
        execution_request,
    ):
        """
        Execute an approved trade and store
        its execution lifecycle.

        A PENDING record is committed before
        contacting the broker. The same record
        is then finalized as EXECUTED or FAILED.

        This provides an audit record if the
        broker accepts an order but the final
        database update cannot be completed.
        """

        execution_mode = (
            self._get_execution_mode()
        )

        demo_execution_enabled = (
            self._is_demo_execution_enabled()
        )

        # ==========================================
        # Create Audit Record Before Broker Call
        # ==========================================

        execution = (
            self.repository.save_execution(
                user_id=user_id,
                symbol=execution_request.symbol,
                direction=execution_request.order_type,
                volume=execution_request.volume,
                status="PENDING",
                broker_order_id=None,
                execution_message=(
                    "Execution started. "
                    "Awaiting broker result."
                ),
            )
        )

        # ==========================================
        # Broker Execution
        # ==========================================

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

            execution_message = (
                result.message
            )

        except Exception as error:
            status = "FAILED"
            order_id = None
            execution_message = str(error)

        # ==========================================
        # Finalize Existing Audit Record
        # ==========================================

        execution = (
            self.repository.update_execution(
                execution=execution,
                status=status,
                broker_order_id=order_id,
                execution_message=execution_message,
            )
        )

        # ==========================================
        # Runtime Execution Information
        # ==========================================
        #
        # These values are not database fields.
        # They describe the current execution
        # environment and are attached to the
        # response object for the API schema.
        #

        execution.execution_mode = (
            execution_mode
        )

        execution.demo_execution_enabled = (
            demo_execution_enabled
        )

        return execution