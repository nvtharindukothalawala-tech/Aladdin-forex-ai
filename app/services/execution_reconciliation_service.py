"""
execution_reconciliation_service.py

Read-only MT5 execution reconciliation service.

Purpose:
- Find local PENDING execution records.
- Inspect MT5 broker evidence.
- Match broker trades using the deterministic
  ALADDIN E<execution_id> comment.
- Repair confirmed local execution records.

Important safety rules:
- Reconciliation is supported only in DEMO mode.
- MOCK mode never claims broker reconciliation.
- Broker data is read-only.
- This service never opens, modifies, or closes trades.
- Symbol, direction, and volume are consistency checks.
- Unmatched or conflicting executions remain PENDING.

Author: Tharindu Kothalawala
Project: Aladdin
"""

import math
import re

from app.services.broker_service import BrokerService


class ExecutionReconciliationService:
    """
    Reconcile local PENDING execution records
    with read-only MT5 broker evidence.
    """

    EXECUTION_COMMENT_PATTERN = re.compile(
        r"^ALADDIN E([1-9]\d*)$"
    )

    def __init__(
        self,
        repository,
    ):
        self.repository = repository

    # ==================================================
    # COMMENT CORRELATION
    # ==================================================

    @classmethod
    def extract_execution_id(
        cls,
        comment,
    ) -> int | None:
        """
        Extract an Aladdin execution ID from an
        exact deterministic MT5 comment.

        Valid example:

            ALADDIN E849

        Legacy comments such as:

            ALADDIN DEMO

        are intentionally not accepted because
        they do not contain a deterministic
        execution ID.
        """

        normalized_comment = (
            str(
                comment
                or ""
            )
            .strip()
            .upper()
        )

        match = (
            cls.EXECUTION_COMMENT_PATTERN.fullmatch(
                normalized_comment
            )
        )

        if match is None:
            return None

        return int(
            match.group(1)
        )

    # ==================================================
    # NORMALIZATION
    # ==================================================

    @staticmethod
    def _normalize_symbol(
        symbol,
    ) -> str:
        """
        Normalize a trading symbol.
        """

        return (
            str(
                symbol
                or ""
            )
            .strip()
            .upper()
        )

    @staticmethod
    def _normalize_direction(
        direction,
    ) -> str:
        """
        Normalize BUY/SELL direction.
        """

        return (
            str(
                direction
                or ""
            )
            .strip()
            .upper()
        )

    @staticmethod
    def _volume_matches(
        local_volume,
        broker_volume,
    ) -> bool:
        """
        Compare execution volume using a small
        floating-point tolerance.
        """

        try:
            local_value = float(
                local_volume
            )

            broker_value = float(
                broker_volume
            )

        except (
            TypeError,
            ValueError,
        ):
            return False

        return math.isclose(
            local_value,
            broker_value,
            rel_tol=0.0,
            abs_tol=1e-8,
        )

    # ==================================================
    # BROKER EVIDENCE
    # ==================================================

    @classmethod
    def _build_open_position_evidence(
        cls,
        broker_positions,
    ) -> list[dict]:
        """
        Convert open MT5 positions into
        reconciliation evidence.

        Open positions provide deterministic
        correlation through their MT5 comment.

        The position ticket is used as the best
        broker identifier available from the
        current open-position monitoring data.
        """

        evidence = []

        for position in broker_positions:

            execution_id = (
                cls.extract_execution_id(
                    position.get(
                        "comment"
                    )
                )
            )

            if execution_id is None:
                continue

            ticket = position.get(
                "ticket"
            )

            broker_order_id = (
                str(ticket)
                if ticket
                else None
            )

            evidence.append(
                {
                    "execution_id": (
                        execution_id
                    ),
                    "source": (
                        "OPEN_POSITION"
                    ),
                    "symbol": (
                        position.get(
                            "symbol"
                        )
                    ),
                    "direction": (
                        position.get(
                            "direction"
                        )
                    ),
                    "volume": (
                        position.get(
                            "volume"
                        )
                    ),
                    "broker_order_id": (
                        broker_order_id
                    ),
                    "position_id": (
                        position.get(
                            "identifier"
                        )
                    ),
                    "comment": (
                        position.get(
                            "comment",
                            "",
                        )
                    ),
                }
            )

        return evidence

    @classmethod
    def _build_closed_trade_evidence(
        cls,
        closed_trades,
    ) -> list[dict]:
        """
        Convert completed MT5 trades into
        reconciliation evidence.

        For completed trades, prefer the original
        opening order ticket because normal MT5
        execution also prefers result.order.

        If the opening order ticket is unavailable,
        use the opening deal ticket as fallback.
        """

        evidence = []

        for trade in closed_trades:

            execution_id = (
                cls.extract_execution_id(
                    trade.get(
                        "comment"
                    )
                )
            )

            if execution_id is None:
                continue

            opening_order_ticket = (
                trade.get(
                    "opening_order_ticket"
                )
            )

            opening_deal_ticket = (
                trade.get(
                    "opening_deal_ticket"
                )
            )

            if opening_order_ticket:

                broker_order_id = str(
                    opening_order_ticket
                )

            elif opening_deal_ticket:

                broker_order_id = str(
                    opening_deal_ticket
                )

            else:

                broker_order_id = None

            evidence.append(
                {
                    "execution_id": (
                        execution_id
                    ),
                    "source": (
                        "CLOSED_TRADE"
                    ),
                    "symbol": (
                        trade.get(
                            "symbol"
                        )
                    ),
                    "direction": (
                        trade.get(
                            "direction"
                        )
                    ),
                    "volume": (
                        trade.get(
                            "volume"
                        )
                    ),
                    "broker_order_id": (
                        broker_order_id
                    ),
                    "position_id": (
                        trade.get(
                            "position_id"
                        )
                    ),
                    "opening_order_ticket": (
                        opening_order_ticket
                    ),
                    "opening_deal_ticket": (
                        opening_deal_ticket
                    ),
                    "comment": (
                        trade.get(
                            "comment",
                            "",
                        )
                    ),
                }
            )

        return evidence

    # ==================================================
    # CONSISTENCY CHECK
    # ==================================================

    @classmethod
    def _get_consistency_errors(
        cls,
        execution,
        evidence,
    ) -> list[str]:
        """
        Compare broker evidence with the local
        PENDING execution.

        Correlation ID is the primary match.

        Symbol, direction, and volume are secondary
        consistency checks.
        """

        errors = []

        local_symbol = (
            cls._normalize_symbol(
                execution.symbol
            )
        )

        broker_symbol = (
            cls._normalize_symbol(
                evidence.get(
                    "symbol"
                )
            )
        )

        if (
            not broker_symbol
            or local_symbol
            != broker_symbol
        ):

            errors.append(
                "Symbol does not match."
            )

        local_direction = (
            cls._normalize_direction(
                execution.direction
            )
        )

        broker_direction = (
            cls._normalize_direction(
                evidence.get(
                    "direction"
                )
            )
        )

        if (
            broker_direction
            not in {
                "BUY",
                "SELL",
            }
            or local_direction
            != broker_direction
        ):

            errors.append(
                "Direction does not match."
            )

        if not cls._volume_matches(
            execution.volume,
            evidence.get(
                "volume"
            ),
        ):

            errors.append(
                "Volume does not match."
            )

        return errors

    # ==================================================
    # RECONCILIATION
    # ==================================================

    def reconcile_pending_executions(
        self,
        user_id: int,
        days: int = 30,
    ) -> dict:
        """
        Reconcile local PENDING executions against
        read-only MT5 DEMO evidence.

        Rules:
        - DEMO mode only.
        - Exact ALADDIN E<ID> correlation required.
        - Matching symbol/direction/volume required.
        - Exactly one broker evidence record required.
        - Confirmed records become EXECUTED.
        - Unmatched records remain PENDING.
        - Conflicting records remain PENDING.
        - No broker trade is modified.
        """

        # ------------------------------------------------
        # Validate user
        # ------------------------------------------------

        if (
            isinstance(
                user_id,
                bool,
            )
            or not isinstance(
                user_id,
                int,
            )
            or user_id <= 0
        ):

            raise ValueError(
                "user_id must be a positive integer."
            )

        # ------------------------------------------------
        # Validate history range
        # ------------------------------------------------

        try:
            history_days = int(
                days
            )

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                "days must be an integer."
            )

        history_days = max(
            1,
            min(
                history_days,
                3650,
            ),
        )

        # ------------------------------------------------
        # DEMO only
        # ------------------------------------------------

        execution_mode = (
            BrokerService.get_execution_mode()
        )

        if execution_mode != "DEMO":

            raise PermissionError(
                "MT5 execution reconciliation "
                "requires DEMO mode."
            )

        # ------------------------------------------------
        # Load local PENDING executions
        # ------------------------------------------------

        pending_executions = (
            self.repository
            .get_pending_executions(
                user_id
            )
        )

        if not pending_executions:

            return {
                "execution_mode": (
                    execution_mode
                ),
                "history_days": (
                    history_days
                ),
                "scanned_pending": 0,
                "reconciled_count": 0,
                "unmatched_count": 0,
                "conflict_count": 0,
                "reconciled": [],
                "unmatched": [],
                "conflicts": [],
                "message": (
                    "No PENDING executions "
                    "require reconciliation."
                ),
            }

        # ------------------------------------------------
        # Read broker evidence
        #
        # These BrokerService operations are read-only.
        # ------------------------------------------------

        positions_result = (
            BrokerService.get_open_positions()
        )

        history_result = (
            BrokerService.get_trade_history(
                days=history_days
            )
        )

        # ------------------------------------------------
        # Safety verification
        # ------------------------------------------------

        if (
            positions_result.get(
                "execution_mode"
            )
            != "DEMO"
        ):

            raise RuntimeError(
                "Open-position broker evidence "
                "did not come from DEMO mode."
            )

        if (
            history_result.get(
                "execution_mode"
            )
            != "DEMO"
        ):

            raise RuntimeError(
                "Trade-history broker evidence "
                "did not come from DEMO mode."
            )

        # ------------------------------------------------
        # Build broker evidence
        # ------------------------------------------------

        open_evidence = (
            self._build_open_position_evidence(
                positions_result.get(
                    "positions",
                    [],
                )
            )
        )

        closed_evidence = (
            self._build_closed_trade_evidence(
                history_result.get(
                    "closed_trades",
                    [],
                )
            )
        )

        all_evidence = (
            open_evidence
            + closed_evidence
        )

        # ------------------------------------------------
        # Group evidence by execution ID
        # ------------------------------------------------

        evidence_by_execution_id = {}

        for evidence in all_evidence:

            execution_id = evidence[
                "execution_id"
            ]

            evidence_by_execution_id.setdefault(
                execution_id,
                [],
            ).append(
                evidence
            )

        # ------------------------------------------------
        # Reconcile each PENDING execution
        # ------------------------------------------------

        reconciled = []
        unmatched = []
        conflicts = []

        for execution in pending_executions:

            execution_id = int(
                execution.id
            )

            matches = (
                evidence_by_execution_id.get(
                    execution_id,
                    [],
                )
            )

            # ============================================
            # No broker evidence
            # ============================================

            if not matches:

                unmatched.append(
                    {
                        "execution_id": (
                            execution_id
                        ),
                        "symbol": (
                            execution.symbol
                        ),
                        "direction": (
                            execution.direction
                        ),
                        "volume": float(
                            execution.volume
                        ),
                        "reason": (
                            "No exact MT5 broker "
                            "correlation was found."
                        ),
                    }
                )

                continue

            # ============================================
            # Ambiguous broker evidence
            # ============================================

            if len(matches) != 1:

                conflicts.append(
                    {
                        "execution_id": (
                            execution_id
                        ),
                        "symbol": (
                            execution.symbol
                        ),
                        "direction": (
                            execution.direction
                        ),
                        "volume": float(
                            execution.volume
                        ),
                        "reason": (
                            "Multiple MT5 broker "
                            "records use the same "
                            "execution correlation ID."
                        ),
                        "evidence_count": (
                            len(matches)
                        ),
                    }
                )

                continue

            evidence = matches[0]

            # ============================================
            # Secondary consistency checks
            # ============================================

            consistency_errors = (
                self._get_consistency_errors(
                    execution,
                    evidence,
                )
            )

            if consistency_errors:

                conflicts.append(
                    {
                        "execution_id": (
                            execution_id
                        ),
                        "symbol": (
                            execution.symbol
                        ),
                        "direction": (
                            execution.direction
                        ),
                        "volume": float(
                            execution.volume
                        ),
                        "evidence_source": (
                            evidence.get(
                                "source"
                            )
                        ),
                        "reason": (
                            "Broker evidence did not "
                            "match the local execution."
                        ),
                        "errors": (
                            consistency_errors
                        ),
                    }
                )

                continue

            # ============================================
            # Broker identifier must exist
            # ============================================

            broker_order_id = (
                evidence.get(
                    "broker_order_id"
                )
            )

            if not broker_order_id:

                conflicts.append(
                    {
                        "execution_id": (
                            execution_id
                        ),
                        "symbol": (
                            execution.symbol
                        ),
                        "direction": (
                            execution.direction
                        ),
                        "volume": float(
                            execution.volume
                        ),
                        "evidence_source": (
                            evidence.get(
                                "source"
                            )
                        ),
                        "reason": (
                            "Exact broker correlation "
                            "was found, but no broker "
                            "identifier was available."
                        ),
                    }
                )

                continue

            # ============================================
            # Confirm local execution
            # ============================================

            updated_execution = (
                self.repository
                .update_execution(
                    execution=execution,
                    status="EXECUTED",
                    broker_order_id=(
                        str(
                            broker_order_id
                        )
                    ),
                    execution_message=(
                        "Execution reconciled from "
                        "read-only MT5 broker evidence."
                    ),
                )
            )

            reconciled.append(
                {
                    "execution_id": int(
                        updated_execution.id
                    ),
                    "symbol": (
                        updated_execution.symbol
                    ),
                    "direction": (
                        updated_execution.direction
                    ),
                    "volume": float(
                        updated_execution.volume
                    ),
                    "broker_order_id": (
                        updated_execution
                        .broker_order_id
                    ),
                    "evidence_source": (
                        evidence.get(
                            "source"
                        )
                    ),
                }
            )

        # ------------------------------------------------
        # Result summary
        # ------------------------------------------------

        return {
            "execution_mode": (
                execution_mode
            ),
            "history_days": (
                history_days
            ),
            "scanned_pending": len(
                pending_executions
            ),
            "reconciled_count": len(
                reconciled
            ),
            "unmatched_count": len(
                unmatched
            ),
            "conflict_count": len(
                conflicts
            ),
            "reconciled": reconciled,
            "unmatched": unmatched,
            "conflicts": conflicts,
            "message": (
                "MT5 execution reconciliation "
                "finished successfully."
            ),
        }