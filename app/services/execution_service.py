"""
execution_service.py

Business logic for trade execution lifecycle.

Author: Tharindu Kothalawala
Project: Aladdin
"""

import hashlib
import json
import os

from sqlalchemy.exc import IntegrityError

from app.execution.execution_manager import (
    ExecutionManager,
)


class ExecutionIdempotencyConflictError(Exception):
    """
    Raised when an idempotency key is reused for a
    different execution request.
    """


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

    @staticmethod
    def _normalize_idempotency_key(
        idempotency_key: str | None,
    ) -> str | None:
        """
        Normalize an optional execution idempotency key.

        Legacy callers may omit the key.

        When supplied, the key must contain meaningful
        text and must fit inside the database column.
        """

        if idempotency_key is None:
            return None

        normalized_key = idempotency_key.strip()

        if not normalized_key:
            raise ValueError(
                "Idempotency key cannot be empty."
            )

        if len(normalized_key) > 128:
            raise ValueError(
                "Idempotency key cannot exceed 128 characters."
            )

        return normalized_key

    @staticmethod
    def _normalize_optional_number(
        value,
    ) -> float | None:
        """
        Normalize an optional broker-relevant numeric value
        before request fingerprinting.
        """

        if value is None:
            return None

        return float(value)

    @classmethod
    def _create_request_fingerprint(
        cls,
        execution_request,
    ) -> str:
        """
        Create a deterministic SHA-256 fingerprint for the
        broker-relevant execution request.

        This prevents the same idempotency key from being
        reused for a different trade payload.
        """

        payload = {
            "symbol": str(
                execution_request.symbol
            ).strip().upper(),
            "direction": str(
                execution_request.order_type
            ).strip().upper(),
            "volume": float(
                execution_request.volume
            ),
            "entry_price": cls._normalize_optional_number(
                getattr(
                    execution_request,
                    "entry_price",
                    None,
                )
            ),
            "stop_loss": cls._normalize_optional_number(
                getattr(
                    execution_request,
                    "stop_loss",
                    None,
                )
            ),
            "take_profit": cls._normalize_optional_number(
                getattr(
                    execution_request,
                    "take_profit",
                    None,
                )
            ),
        }

        canonical_payload = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(
            canonical_payload.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _verify_existing_fingerprint(
        execution,
        request_fingerprint: str,
    ):
        """
        Verify that an existing idempotent execution belongs
        to the same execution request.

        A matching key with a different payload is rejected.
        """

        if (
            execution.request_fingerprint
            != request_fingerprint
        ):
            raise ExecutionIdempotencyConflictError(
                "This idempotency key has already been used "
                "for a different execution request."
            )

    @staticmethod
    def _attach_runtime_information(
        execution,
        execution_mode: str,
        demo_execution_enabled: bool,
    ):
        """
        Attach non-persistent execution environment fields
        used by the API response.
        """

        execution.execution_mode = (
            execution_mode
        )

        execution.demo_execution_enabled = (
            demo_execution_enabled
        )

        return execution

    def _get_existing_idempotent_execution(
        self,
        user_id: int,
        idempotency_key: str,
        request_fingerprint: str,
    ):
        """
        Return an existing matching execution when the same
        user and idempotency key have already been recorded.

        If the key belongs to a different request payload,
        raise an explicit conflict.
        """

        execution = (
            self.repository
            .get_execution_by_idempotency_key(
                user_id=user_id,
                idempotency_key=idempotency_key,
            )
        )

        if execution is None:
            return None

        self._verify_existing_fingerprint(
            execution=execution,
            request_fingerprint=request_fingerprint,
        )

        return execution

    def execute_trade(
        self,
        user_id: int,
        execution_request,
        idempotency_key: str | None = None,
    ):
        """
        Execute an approved trade and store
        its execution lifecycle.

        A PENDING record is committed before
        contacting the broker.

        When an idempotency key is supplied,
        duplicate requests return the existing
        execution record without contacting MT5
        again.

        The database execution ID is then
        attached to the execution request so
        MT5 can store the same reference in
        the broker order comment.

        Example:

            Database execution ID:
                123

            MT5 comment:
                ALADDIN E123

        This allows a PENDING execution to be
        correlated with MT5 if the broker order
        succeeds but the final database update
        fails.
        """

        execution_mode = (
            self._get_execution_mode()
        )

        demo_execution_enabled = (
            self._is_demo_execution_enabled()
        )

        normalized_idempotency_key = (
            self._normalize_idempotency_key(
                idempotency_key
            )
        )

        request_fingerprint = None

        # ==========================================
        # Idempotency Pre-Check
        # ==========================================

        if normalized_idempotency_key is not None:
            request_fingerprint = (
                self._create_request_fingerprint(
                    execution_request
                )
            )

            existing_execution = (
                self._get_existing_idempotent_execution(
                    user_id=user_id,
                    idempotency_key=(
                        normalized_idempotency_key
                    ),
                    request_fingerprint=(
                        request_fingerprint
                    ),
                )
            )

            if existing_execution is not None:
                return (
                    self._attach_runtime_information(
                        execution=existing_execution,
                        execution_mode=execution_mode,
                        demo_execution_enabled=(
                            demo_execution_enabled
                        ),
                    )
                )

        # ==========================================
        # Create Audit Record Before Broker Call
        # ==========================================
        #
        # The database unique index on:
        #
        #   user_id + idempotency_key
        #
        # is the final protection against two
        # simultaneous requests creating duplicate
        # execution records.
        #

        try:
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
                    idempotency_key=(
                        normalized_idempotency_key
                    ),
                    request_fingerprint=(
                        request_fingerprint
                    ),
                )
            )

        except IntegrityError:
            if normalized_idempotency_key is None:
                raise

            existing_execution = (
                self._get_existing_idempotent_execution(
                    user_id=user_id,
                    idempotency_key=(
                        normalized_idempotency_key
                    ),
                    request_fingerprint=(
                        request_fingerprint
                    ),
                )
            )

            if existing_execution is None:
                raise

            return (
                self._attach_runtime_information(
                    execution=existing_execution,
                    execution_mode=execution_mode,
                    demo_execution_enabled=(
                        demo_execution_enabled
                    ),
                )
            )

        # ==========================================
        # Attach Correlation ID
        # ==========================================
        #
        # The PENDING execution has already been
        # committed, so execution.id is stable.
        #
        # This ID is passed through the execution
        # pipeline and written into the MT5 order
        # comment.
        #

        execution_request.execution_id = (
            execution.id
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

        return (
            self._attach_runtime_information(
                execution=execution,
                execution_mode=execution_mode,
                demo_execution_enabled=(
                    demo_execution_enabled
                ),
            )
        )