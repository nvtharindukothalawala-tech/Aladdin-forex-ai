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

from app.execution.execution_safety_context import (
    ExecutionSafetyContext,
)

from app.services.execution_safety_service import (
    ExecutionSafetyService,
)


class ExecutionIdempotencyConflictError(Exception):
    """
    Raised when an idempotency key is reused for a
    different execution request.
    """


class ExecutionSafetyRejectedError(Exception):
    """
    Raised when the deterministic execution safety
    gate rejects a trade before broker execution.
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

    # ======================================================
    # EXECUTION ENVIRONMENT
    # ======================================================

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

    # ======================================================
    # IDEMPOTENCY HELPERS
    # ======================================================

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
        Normalize an optional broker-relevant numeric
        value before request fingerprinting or audit
        persistence.
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
        Create a deterministic SHA-256 fingerprint for
        the broker-relevant execution request.

        This prevents the same idempotency key from
        being reused for a different trade payload.
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
            "entry_price": (
                cls._normalize_optional_number(
                    getattr(
                        execution_request,
                        "entry_price",
                        None,
                    )
                )
            ),
            "stop_loss": (
                cls._normalize_optional_number(
                    getattr(
                        execution_request,
                        "stop_loss",
                        None,
                    )
                )
            ),
            "take_profit": (
                cls._normalize_optional_number(
                    getattr(
                        execution_request,
                        "take_profit",
                        None,
                    )
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
        Verify that an existing idempotent execution
        belongs to the same execution request.

        A matching key with a different payload is
        rejected.
        """

        if (
            execution.request_fingerprint
            != request_fingerprint
        ):
            raise ExecutionIdempotencyConflictError(
                "This idempotency key has already been used "
                "for a different execution request."
            )

    # ======================================================
    # RESPONSE RUNTIME INFORMATION
    # ======================================================

    @staticmethod
    def _attach_runtime_information(
        execution,
        execution_mode: str,
        demo_execution_enabled: bool,
    ):
        """
        Attach non-persistent execution environment
        fields used by the API response.
        """

        execution.execution_mode = (
            execution_mode
        )

        execution.demo_execution_enabled = (
            demo_execution_enabled
        )

        return execution

    # ======================================================
    # IDEMPOTENT EXECUTION LOOKUP
    # ======================================================

    def _get_existing_idempotent_execution(
        self,
        user_id: int,
        idempotency_key: str,
        request_fingerprint: str,
    ):
        """
        Return an existing matching execution when
        the same user and idempotency key have
        already been recorded.

        If the key belongs to a different request
        payload, raise an explicit conflict.
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

    # ======================================================
    # DETERMINISTIC EXECUTION SAFETY GATE
    # ======================================================

    @staticmethod
    def _run_execution_safety_gate(
        execution_request,
        safety_context: ExecutionSafetyContext,
        execution_mode: str,
        demo_execution_enabled: bool,
    ) -> dict:
        """
        Run the deterministic final execution safety
        gate.

        The gate runs before a PENDING execution
        record is created and before MT5 is contacted.

        An approved result is bound to the exact
        validated:

        - symbol
        - direction
        - volume
        - entry price
        - stop loss
        - take profit
        """

        safety_result = (
            ExecutionSafetyService.analyze(
                trade_setup=(
                    safety_context.trade_setup
                ),
                risk=(
                    safety_context.risk
                ),
                quote=(
                    safety_context.quote
                ),
                symbol_info=(
                    safety_context.symbol_info
                ),
                execution_mode=execution_mode,
                demo_execution_enabled=(
                    demo_execution_enabled
                ),
            )
        )

        # --------------------------------------------------
        # Safety Decision
        # --------------------------------------------------

        if not safety_result.get(
            "approved",
            False,
        ):
            reason = ""

            reasons = safety_result.get(
                "reasons"
            )

            if isinstance(
                reasons,
                (list, tuple),
            ):
                reason = "; ".join(
                    str(item).strip()
                    for item in reasons
                    if str(item).strip()
                )

            elif reasons is not None:
                reason = str(
                    reasons
                ).strip()

            # Backward compatibility with older
            # safety-result contracts.
            if not reason:
                legacy_reason = (
                    safety_result.get(
                        "reason"
                    )
                )

                if legacy_reason is not None:
                    reason = str(
                        legacy_reason
                    ).strip()

            if not reason:
                reason = (
                    "Execution safety gate "
                    "rejected trade."
                )

            raise ExecutionSafetyRejectedError(
                reason
            )

        # --------------------------------------------------
        # Retrieve Approved Execution Binding
        # --------------------------------------------------

        raw_binding = safety_result.get(
            "execution_binding"
        )

        if raw_binding is None:

            binding = {
                key: safety_result.get(key)
                for key in (
                    "symbol",
                    "direction",
                    "volume",
                    "entry_price",
                    "stop_loss",
                    "take_profit",
                )
                if safety_result.get(key)
                is not None
            }

        elif isinstance(
            raw_binding,
            dict,
        ):
            binding = raw_binding

        else:
            raise ExecutionSafetyRejectedError(
                "Execution safety binding is invalid."
            )

        # --------------------------------------------------
        # Symbol Binding
        # --------------------------------------------------

        safety_symbol = binding.get(
            "symbol"
        )

        if safety_symbol is not None:

            normalized_safety_symbol = (
                str(safety_symbol)
                .replace("/", "")
                .strip()
                .upper()
            )

            normalized_request_symbol = (
                str(
                    execution_request.symbol
                )
                .replace("/", "")
                .strip()
                .upper()
            )

            if (
                normalized_safety_symbol
                and normalized_safety_symbol
                != normalized_request_symbol
            ):
                raise ExecutionSafetyRejectedError(
                    "Execution symbol does not match "
                    "the approved safety analysis."
                )

        # --------------------------------------------------
        # Direction Binding
        # --------------------------------------------------

        safety_direction = binding.get(
            "direction"
        )

        if safety_direction is not None:

            normalized_safety_direction = (
                str(safety_direction)
                .strip()
                .upper()
            )

            normalized_request_direction = (
                str(
                    execution_request.order_type
                )
                .strip()
                .upper()
            )

            if (
                normalized_safety_direction
                and normalized_safety_direction
                != normalized_request_direction
            ):
                raise ExecutionSafetyRejectedError(
                    "Execution direction does not match "
                    "the approved safety analysis."
                )

        # --------------------------------------------------
        # Numeric Binding Helper
        # --------------------------------------------------

        def verify_numeric_binding(
            binding_key: str,
            request_attribute: str,
            label: str,
        ) -> None:
            """
            Verify one numeric safety binding against
            the prepared execution request.
            """

            safety_value = binding.get(
                binding_key
            )

            if safety_value is None:
                return

            request_value = getattr(
                execution_request,
                request_attribute,
                None,
            )

            if request_value is None:
                raise ExecutionSafetyRejectedError(
                    f"Execution {label} does not match "
                    "the approved safety analysis."
                )

            try:
                normalized_safety_value = float(
                    safety_value
                )

                normalized_request_value = float(
                    request_value
                )

            except (
                TypeError,
                ValueError,
            ) as error:
                raise ExecutionSafetyRejectedError(
                    f"Execution {label} binding is invalid."
                ) from error

            tolerance = max(
                1e-9,
                abs(
                    normalized_safety_value
                )
                * 1e-12,
            )

            if (
                abs(
                    normalized_safety_value
                    - normalized_request_value
                )
                > tolerance
            ):
                raise ExecutionSafetyRejectedError(
                    f"Execution {label} does not match "
                    "the approved safety analysis."
                )

        # --------------------------------------------------
        # Verify All Numeric Bindings
        # --------------------------------------------------

        verify_numeric_binding(
            "volume",
            "volume",
            "volume",
        )

        verify_numeric_binding(
            "entry_price",
            "entry_price",
            "entry price",
        )

        verify_numeric_binding(
            "stop_loss",
            "stop_loss",
            "stop loss",
        )

        verify_numeric_binding(
            "take_profit",
            "take_profit",
            "take profit",
        )

        return safety_result

    # ======================================================
    # SAFETY AUDIT SERIALIZATION
    # ======================================================

    @staticmethod
    def _serialize_safety_audit_value(
        value,
    ) -> str:
        """
        Serialize deterministic safety information
        into canonical JSON for audit persistence.

        default=str protects audit persistence from
        unexpected non-JSON-native scalar values while
        retaining deterministic key ordering.
        """

        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )

    def _save_execution_safety_audit(
        self,
        *,
        execution,
        user_id: int,
        execution_request,
        safety_result: dict,
        execution_mode: str,
    ):
        """
        Persist the approved deterministic safety
        snapshot associated with an execution.

        This method must run after the PENDING
        execution record exists but before MT5 is
        contacted.

        If persistence fails, the exception is
        intentionally propagated so broker execution
        does not continue without an audit record.
        """

        checks = (
            safety_result.get("checks")
            or {}
        )

        reasons = (
            safety_result.get("reasons")
            or []
        )

        limits = (
            safety_result.get("limits")
            or {}
        )

        safety_status = str(
            safety_result.get(
                "status",
                "APPROVED",
            )
        ).strip().upper()

        if not safety_status:
            safety_status = "APPROVED"

        safety_engine = str(
            safety_result.get(
                "engine",
                "DETERMINISTIC",
            )
        ).strip().upper()

        if not safety_engine:
            safety_engine = "DETERMINISTIC"

        return (
            self.repository.save_safety_audit(
                execution_id=execution.id,
                user_id=user_id,
                safety_status=safety_status,
                safety_engine=safety_engine,
                execution_mode=(
                    execution_mode
                ),
                symbol=str(
                    execution_request.symbol
                ),
                direction=str(
                    execution_request.order_type
                ),
                volume=float(
                    execution_request.volume
                ),
                entry_price=(
                    self._normalize_optional_number(
                        getattr(
                            execution_request,
                            "entry_price",
                            None,
                        )
                    )
                ),
                stop_loss=(
                    self._normalize_optional_number(
                        getattr(
                            execution_request,
                            "stop_loss",
                            None,
                        )
                    )
                ),
                take_profit=(
                    self._normalize_optional_number(
                        getattr(
                            execution_request,
                            "take_profit",
                            None,
                        )
                    )
                ),
                checks_json=(
                    self._serialize_safety_audit_value(
                        checks
                    )
                ),
                reasons_json=(
                    self._serialize_safety_audit_value(
                        reasons
                    )
                ),
                limits_json=(
                    self._serialize_safety_audit_value(
                        limits
                    )
                ),
            )
        )

    # ======================================================
    # EXECUTE TRADE
    # ======================================================

    def execute_trade(
        self,
        user_id: int,
        execution_request,
        idempotency_key: str | None = None,
        safety_context: (
            ExecutionSafetyContext
            | None
        ) = None,
    ):
        """
        Execute an approved trade and store its
        execution lifecycle.

        Lifecycle:

            1. Resolve execution environment.
            2. Validate idempotency.
            3. Return existing idempotent execution
               when applicable.
            4. Run deterministic safety gate.
            5. Create PENDING execution record.
            6. Persist approved safety audit snapshot.
            7. Attach execution correlation ID.
            8. Contact MT5.
            9. Finalize execution as EXECUTED or FAILED.

        The safety context remains optional during
        migration so legacy callers continue to work.

        New deterministic execution callers should
        provide a safety context.

        When an idempotency key is supplied, duplicate
        requests return the existing execution without
        rerunning safety analysis, creating another
        audit snapshot, or contacting MT5 again.
        """

        # ==========================================
        # Execution Environment
        # ==========================================

        execution_mode = (
            self._get_execution_mode()
        )

        demo_execution_enabled = (
            self._is_demo_execution_enabled()
        )

        # ==========================================
        # Normalize Idempotency Key
        # ==========================================

        normalized_idempotency_key = (
            self._normalize_idempotency_key(
                idempotency_key
            )
        )

        request_fingerprint = None

        # ==========================================
        # Idempotency Pre-Check
        # ==========================================

        if (
            normalized_idempotency_key
            is not None
        ):
            request_fingerprint = (
                self._create_request_fingerprint(
                    execution_request
                )
            )

            existing_execution = (
                self
                ._get_existing_idempotent_execution(
                    user_id=user_id,
                    idempotency_key=(
                        normalized_idempotency_key
                    ),
                    request_fingerprint=(
                        request_fingerprint
                    ),
                )
            )

            if (
                existing_execution
                is not None
            ):
                return (
                    self
                    ._attach_runtime_information(
                        execution=(
                            existing_execution
                        ),
                        execution_mode=(
                            execution_mode
                        ),
                        demo_execution_enabled=(
                            demo_execution_enabled
                        ),
                    )
                )

        # ==========================================
        # Deterministic Execution Safety Gate
        # ==========================================
        #
        # IMPORTANT:
        #
        # Safety runs before:
        #
        # - PENDING execution creation
        # - safety audit creation
        # - execution correlation ID assignment
        # - MT5 execution
        #
        # Therefore a rejected trade cannot reach
        # the broker.
        #
        # Idempotent replays returned above and do
        # not rerun the safety gate.
        # ==========================================

        safety_result = None

        if safety_context is not None:

            safety_result = (
                self._run_execution_safety_gate(
                    execution_request=(
                        execution_request
                    ),
                    safety_context=(
                        safety_context
                    ),
                    execution_mode=(
                        execution_mode
                    ),
                    demo_execution_enabled=(
                        demo_execution_enabled
                    ),
                )
            )

        # ==========================================
        # Create PENDING Execution Record
        # ==========================================
        #
        # The database unique index on:
        #
        #   user_id + idempotency_key
        #
        # provides final protection against two
        # simultaneous requests creating duplicate
        # execution records.
        # ==========================================

        try:

            execution = (
                self.repository.save_execution(
                    user_id=user_id,
                    symbol=(
                        execution_request.symbol
                    ),
                    direction=(
                        execution_request.order_type
                    ),
                    volume=(
                        execution_request.volume
                    ),
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

            # --------------------------------------
            # Non-idempotent requests should never
            # consume an idempotency collision.
            # --------------------------------------

            if (
                normalized_idempotency_key
                is None
            ):
                raise

            # --------------------------------------
            # Another concurrent request may have
            # created the execution after our
            # initial pre-check.
            # --------------------------------------

            existing_execution = (
                self
                ._get_existing_idempotent_execution(
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

            # --------------------------------------
            # The concurrent request owns the
            # execution lifecycle. Do not create
            # another audit and do not call MT5.
            # --------------------------------------

            return (
                self._attach_runtime_information(
                    execution=(
                        existing_execution
                    ),
                    execution_mode=(
                        execution_mode
                    ),
                    demo_execution_enabled=(
                        demo_execution_enabled
                    ),
                )
            )

        # ==========================================
        # Persist Approved Safety Audit
        # ==========================================
        #
        # The execution ID is now stable because the
        # PENDING execution has been committed.
        #
        # The safety audit MUST be stored before MT5
        # is contacted.
        #
        # If safety-audit persistence fails, the
        # exception intentionally propagates and
        # broker execution is stopped.
        #
        # Legacy executions without a safety context
        # continue without a safety audit.
        # ==========================================

        if safety_result is not None:

            self._save_execution_safety_audit(
                execution=execution,
                user_id=user_id,
                execution_request=(
                    execution_request
                ),
                safety_result=(
                    safety_result
                ),
                execution_mode=(
                    execution_mode
                ),
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
        # Example:
        #
        #     Database execution ID:
        #         123
        #
        #     MT5 comment:
        #         ALADDIN E123
        #
        # This allows reconciliation if the broker
        # succeeds but the final database update
        # fails.
        # ==========================================

        execution_request.execution_id = (
            execution.id
        )

        # ==========================================
        # Broker Execution
        # ==========================================

        try:

            result = (
                ExecutionManager
                .execute_with_mt5(
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

            # --------------------------------------
            # Broker exceptions are converted into
            # FAILED execution history records.
            #
            # This preserves the existing lifecycle
            # and provides an auditable failure.
            # --------------------------------------

            status = "FAILED"

            order_id = None

            execution_message = str(
                error
            )

        # ==========================================
        # Finalize Existing Execution Record
        # ==========================================

        execution = (
            self.repository.update_execution(
                execution=execution,
                status=status,
                broker_order_id=order_id,
                execution_message=(
                    execution_message
                ),
            )
        )

        # ==========================================
        # Runtime Execution Information
        # ==========================================

        return (
            self._attach_runtime_information(
                execution=execution,
                execution_mode=(
                    execution_mode
                ),
                demo_execution_enabled=(
                    demo_execution_enabled
                ),
            )
        )