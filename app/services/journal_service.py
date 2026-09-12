"""
journal_service.py

Handles journal business logic.

Supports:
- Reading user journal trades
- Counting journal trades
- Importing completed MT5 DEMO positions
  into the Aladdin trade journal

The MT5 synchronization is read-only from
the broker side. It does not open, modify,
or close any MT5 trade.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from datetime import datetime

from app.services.broker_service import BrokerService


class JournalService:
    """
    Provides journal operations.
    """

    def __init__(
        self,
        repository,
    ):
        self.repository = repository

    # ======================================================
    # GET JOURNAL TRADES
    # ======================================================

    def get_trades(
        self,
        user_id: int,
    ):
        """
        Return trades belonging to a user.
        """

        return self.repository.get_user_trades(
            user_id
        )

    # ======================================================
    # GET JOURNAL TRADE COUNT
    # ======================================================

    def get_trade_count(
        self,
        user_id: int,
    ):
        """
        Return trade count for a user.
        """

        return self.repository.count_user_trades(
            user_id
        )

    # ======================================================
    # SYNC MT5 COMPLETED POSITIONS
    # ======================================================

    def sync_mt5_closed_trades(
        self,
        user_id: int,
        days: int = 30,
        include_other_trades: bool = False,
    ) -> dict:
        """
        Import completed MT5 positions into
        the Aladdin journal.

        By default, only trades identified as
        Aladdin trades are imported.

        Duplicate imports are prevented by
        the repository using the final MT5
        closing deal ticket.
        """

        # --------------------------------------------------
        # Validate user
        # --------------------------------------------------

        if user_id <= 0:
            raise ValueError(
                "user_id must be greater than zero."
            )

        # --------------------------------------------------
        # Validate history range
        # --------------------------------------------------

        days = max(
            1,
            min(
                int(days),
                3650,
            ),
        )

        # --------------------------------------------------
        # Load completed positions from broker history
        # --------------------------------------------------

        broker_history = (
            BrokerService.get_trade_history(
                days=days
            )
        )

        closed_trades = (
            broker_history.get(
                "closed_trades",
                [],
            )
        )

        imported_count = 0
        duplicate_count = 0
        skipped_count = 0

        imported_trades = []
        skipped_trades = []

        # --------------------------------------------------
        # Process completed MT5 positions
        # --------------------------------------------------

        for trade in closed_trades:

            # ==============================================
            # Check whether trade belongs to Aladdin
            # ==============================================

            is_aladdin_trade = bool(
                trade.get(
                    "is_aladdin_trade",
                    False,
                )
            )

            if (
                not include_other_trades
                and not is_aladdin_trade
            ):

                skipped_count += 1

                skipped_trades.append(
                    {
                        "deal_ticket": (
                            trade.get(
                                "deal_ticket"
                            )
                        ),
                        "position_id": (
                            trade.get(
                                "position_id"
                            )
                        ),
                        "symbol": (
                            trade.get(
                                "symbol"
                            )
                        ),
                        "reason": (
                            "Not identified as "
                            "an Aladdin trade."
                        ),
                    }
                )

                continue

            # ==============================================
            # Required identifiers
            # ==============================================

            deal_ticket = trade.get(
                "deal_ticket"
            )

            order_ticket = trade.get(
                "order_ticket"
            )

            position_id = trade.get(
                "position_id"
            )

            if not deal_ticket:

                skipped_count += 1

                skipped_trades.append(
                    {
                        "position_id": (
                            position_id
                        ),
                        "symbol": (
                            trade.get(
                                "symbol"
                            )
                        ),
                        "reason": (
                            "Missing MT5 deal ticket."
                        ),
                    }
                )

                continue

            # ==============================================
            # Validate direction
            # ==============================================

            direction = (
                str(
                    trade.get(
                        "direction",
                        "",
                    )
                )
                .strip()
                .upper()
            )

            if direction not in {
                "BUY",
                "SELL",
            }:

                skipped_count += 1

                skipped_trades.append(
                    {
                        "deal_ticket": (
                            deal_ticket
                        ),
                        "position_id": (
                            position_id
                        ),
                        "symbol": (
                            trade.get(
                                "symbol"
                            )
                        ),
                        "reason": (
                            "Invalid trade direction."
                        ),
                    }
                )

                continue

            # ==============================================
            # Validate symbol
            # ==============================================

            symbol = (
                str(
                    trade.get(
                        "symbol",
                        "",
                    )
                )
                .strip()
                .upper()
            )

            if not symbol:

                skipped_count += 1

                skipped_trades.append(
                    {
                        "deal_ticket": (
                            deal_ticket
                        ),
                        "position_id": (
                            position_id
                        ),
                        "reason": (
                            "Missing symbol."
                        ),
                    }
                )

                continue

            # ==============================================
            # Parse MT5 close time
            # ==============================================

            closed_at = None

            trade_time = trade.get(
                "time"
            )

            if trade_time:

                try:

                    closed_at = (
                        datetime.fromisoformat(
                            trade_time
                        )
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    closed_at = None

            # ==============================================
            # Financial values
            # ==============================================

            profit = float(
                trade.get(
                    "profit",
                    0.0,
                )
                or 0.0
            )

            commission = float(
                trade.get(
                    "commission",
                    0.0,
                )
                or 0.0
            )

            swap = float(
                trade.get(
                    "swap",
                    0.0,
                )
                or 0.0
            )

            fee = float(
                trade.get(
                    "fee",
                    0.0,
                )
                or 0.0
            )

            close_price = float(
                trade.get(
                    "close_price",
                    0.0,
                )
                or 0.0
            )

            # ==============================================
            # Save using TradeRepository
            # ==============================================

            db_trade, was_created = (
                self.repository
                .save_mt5_closed_trade(
                    user_id=user_id,
                    deal_ticket=int(
                        deal_ticket
                    ),
                    order_ticket=(
                        int(order_ticket)
                        if order_ticket
                        else None
                    ),
                    position_id=(
                        int(position_id)
                        if position_id
                        else None
                    ),
                    symbol=symbol,
                    direction=direction,
                    close_price=close_price,
                    profit=profit,
                    commission=commission,
                    swap=swap,
                    fee=fee,
                    closed_at=closed_at,
                    is_aladdin_trade=(
                        is_aladdin_trade
                    ),
                    risk_reward=None,
                )
            )

            # ==============================================
            # New journal import
            # ==============================================

            if was_created:

                imported_count += 1

                imported_trades.append(
                    {
                        "journal_id": int(
                            db_trade.id
                        ),
                        "deal_ticket": int(
                            deal_ticket
                        ),
                        "position_id": (
                            int(position_id)
                            if position_id
                            else None
                        ),
                        "symbol": symbol,
                        "direction": direction,
                        "profit_loss": float(
                            db_trade.profit_loss
                        ),
                    }
                )

            # ==============================================
            # Existing journal record
            # ==============================================

            else:

                duplicate_count += 1

        # --------------------------------------------------
        # Return synchronization summary
        # --------------------------------------------------

        return {
            "execution_mode": (
                broker_history.get(
                    "execution_mode"
                )
            ),
            "history_days": days,
            "broker_closed_trade_count": (
                len(
                    closed_trades
                )
            ),
            "imported_count": (
                imported_count
            ),
            "duplicate_count": (
                duplicate_count
            ),
            "skipped_count": (
                skipped_count
            ),
            "include_other_trades": (
                include_other_trades
            ),
            "imported_trades": (
                imported_trades
            ),
            "skipped_trades": (
                skipped_trades
            ),
            "message": (
                "MT5 completed-position "
                "journal synchronization "
                "finished successfully."
            ),
        }