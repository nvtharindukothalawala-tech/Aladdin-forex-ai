"""
repository.py

Database operations for execution history.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from app.execution.models import ExecutionModel


class ExecutionRepository:
    """
    Handles execution database operations.
    """

    def __init__(
        self,
        session,
    ):
        self.session = session

    def save_execution(
        self,
        user_id: int,
        symbol: str,
        direction: str,
        volume: float,
        status: str,
        broker_order_id: str | None = None,
        execution_message: str | None = None,
    ):
        """
        Create and persist a new execution record.
        """

        execution = ExecutionModel(
            user_id=user_id,
            symbol=symbol,
            direction=direction,
            volume=volume,
            status=status,
            broker_order_id=broker_order_id,
            execution_message=execution_message,
        )

        try:
            self.session.add(execution)
            self.session.commit()
            self.session.refresh(execution)

            return execution

        except Exception:
            self.session.rollback()
            raise

    def update_execution(
        self,
        execution,
        status: str,
        broker_order_id: str | None = None,
        execution_message: str | None = None,
    ):
        """
        Update an existing execution record.

        The execution is created before the broker
        call as PENDING and finalized after the
        broker result is known.
        """

        execution.status = status
        execution.broker_order_id = broker_order_id
        execution.execution_message = execution_message

        try:
            self.session.commit()
            self.session.refresh(execution)

            return execution

        except Exception:
            self.session.rollback()
            raise

    def get_user_executions(
        self,
        user_id: int,
    ):
        """
        Return executions for a user.
        """

        return (
            self.session.query(ExecutionModel)
            .filter(
                ExecutionModel.user_id == user_id
            )
            .all()
        )

    def count_user_executions(
        self,
        user_id: int,
    ):
        """
        Count executions for a user.
        """

        return (
            self.session.query(ExecutionModel)
            .filter(
                ExecutionModel.user_id == user_id
            )
            .count()
        )