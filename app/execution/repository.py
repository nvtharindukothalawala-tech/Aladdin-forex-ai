"""
repository.py

Database operations for execution history.

Author: Tharindu Kothalwala
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
    ):
        """
        Save execution result.
        """

        execution = ExecutionModel(
            user_id=user_id,
            symbol=symbol,
            direction=direction,
            volume=volume,
            status=status,
            broker_order_id=broker_order_id,
        )

        self.session.add(execution)

        self.session.commit()

        self.session.refresh(execution)

        return execution

    def get_user_executions(
        self,
        user_id: int,
    ):
        """
        Return executions for a user.
        """

        return (
            self.session.query(ExecutionModel)
            .filter(ExecutionModel.user_id == user_id)
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
            .filter(ExecutionModel.user_id == user_id)
            .count()
        )
