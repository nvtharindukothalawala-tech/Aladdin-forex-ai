"""
repository.py

Database operations for execution history and
execution-safety audit snapshots.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from app.execution.models import (
    ExecutionModel,
    ExecutionSafetyAuditModel,
)


class ExecutionRepository:
    """
    Handles execution database operations.
    """

    def __init__(
        self,
        session,
    ):
        self.session = session

    # ==================================================
    # EXECUTION CREATE
    # ==================================================

    def save_execution(
        self,
        user_id: int,
        symbol: str,
        direction: str,
        volume: float,
        status: str,
        broker_order_id: str | None = None,
        execution_message: str | None = None,
        idempotency_key: str | None = None,
        request_fingerprint: str | None = None,
    ):
        """
        Create and persist a new execution record.

        The idempotency fields are optional so legacy execution
        requests continue to work.

        When an idempotency key is supplied, the database unique
        index on user_id + idempotency_key prevents two records
        from being created for the same logical execution attempt.
        """

        execution = ExecutionModel(
            user_id=user_id,
            symbol=symbol,
            direction=direction,
            volume=volume,
            status=status,
            broker_order_id=broker_order_id,
            execution_message=execution_message,
            idempotency_key=idempotency_key,
            request_fingerprint=request_fingerprint,
        )

        try:
            self.session.add(execution)
            self.session.commit()
            self.session.refresh(execution)

            return execution

        except Exception:
            self.session.rollback()
            raise

    # ==================================================
    # EXECUTION UPDATE
    # ==================================================

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

    # ==================================================
    # IDEMPOTENCY LOOKUP
    # ==================================================

    def get_execution_by_idempotency_key(
        self,
        user_id: int,
        idempotency_key: str,
    ):
        """
        Return one execution matching the user's idempotency key.

        The database unique index guarantees that at most one
        execution can exist for the same user and key.
        """

        return (
            self.session.query(ExecutionModel)
            .filter(
                ExecutionModel.user_id == user_id,
                ExecutionModel.idempotency_key == idempotency_key,
            )
            .one_or_none()
        )

    # ==================================================
    # EXECUTION READ OPERATIONS
    # ==================================================

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

    def get_pending_executions(
        self,
        user_id: int,
    ):
        """
        Return PENDING executions for a user.

        These records may require broker
        reconciliation if MT5 execution completed
        but the final database update failed.

        Oldest records are returned first so the
        reconciliation order is deterministic.
        """

        return (
            self.session.query(ExecutionModel)
            .filter(
                ExecutionModel.user_id == user_id,
                ExecutionModel.status == "PENDING",
            )
            .order_by(
                ExecutionModel.id.asc()
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

    # ==================================================
    # EXECUTION SAFETY AUDIT
    # ==================================================

    def save_safety_audit(
        self,
        *,
        execution_id: int,
        user_id: int,
        safety_status: str,
        safety_engine: str,
        execution_mode: str,
        symbol: str,
        direction: str,
        volume: float,
        entry_price: float | None,
        stop_loss: float | None,
        take_profit: float | None,
        checks_json: str,
        reasons_json: str,
        limits_json: str,
    ):
        """
        Persist the deterministic safety snapshot associated
        with one execution.

        The unique index on execution_id guarantees that one
        execution can have at most one safety audit snapshot.
        """

        audit = ExecutionSafetyAuditModel(
            execution_id=execution_id,
            user_id=user_id,
            safety_status=safety_status,
            safety_engine=safety_engine,
            execution_mode=execution_mode,
            symbol=symbol,
            direction=direction,
            volume=volume,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            checks_json=checks_json,
            reasons_json=reasons_json,
            limits_json=limits_json,
        )

        try:
            self.session.add(audit)
            self.session.commit()
            self.session.refresh(audit)

            return audit

        except Exception:
            self.session.rollback()
            raise

    def get_safety_audit_by_execution_id(
        self,
        execution_id: int,
    ):
        """
        Return the safety audit snapshot associated
        with one execution.
        """

        return (
            self.session.query(
                ExecutionSafetyAuditModel
            )
            .filter(
                ExecutionSafetyAuditModel.execution_id
                == execution_id
            )
            .one_or_none()
        )

    def get_user_safety_audits(
        self,
        user_id: int,
    ):
        """
        Return all safety audit snapshots belonging
        to one user.

        Oldest records are returned first to keep
        retrieval deterministic.
        """

        return (
            self.session.query(
                ExecutionSafetyAuditModel
            )
            .filter(
                ExecutionSafetyAuditModel.user_id
                == user_id
            )
            .order_by(
                ExecutionSafetyAuditModel.id.asc()
            )
            .all()
        )

    def count_user_safety_audits(
        self,
        user_id: int,
    ):
        """
        Count safety audit snapshots belonging
        to one user.
        """

        return (
            self.session.query(
                ExecutionSafetyAuditModel
            )
            .filter(
                ExecutionSafetyAuditModel.user_id
                == user_id
            )
            .count()
        )
