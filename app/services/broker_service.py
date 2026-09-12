"""
broker_service.py

Read-only MT5 broker monitoring service.

Provides:
- MT5 connection status
- DEMO account information
- Open positions
- Completed trade history

This service does NOT create, modify,
or close any trades.

Author: Tharindu Kothalawala
Project: Aladdin
"""

import os
from datetime import (
    datetime,
    timedelta,
    timezone,
)

import MetaTrader5 as mt5

from app.mt5.mt5_connector import MT5Connector


class BrokerService:
    """
    Provides read-only broker information.

    Supported modes:
    - MOCK
    - DEMO

    LIVE accounts remain blocked by
    the existing MT5Connector.
    """

    # ======================================================
    # EXECUTION ENVIRONMENT
    # ======================================================

    @staticmethod
    def get_execution_mode() -> str:
        """
        Return the configured MT5 mode.
        """

        return (
            os.getenv(
                "ALADDIN_MT5_MODE",
                "MOCK",
            )
            .strip()
            .upper()
        )

    @staticmethod
    def is_demo_execution_enabled() -> bool:
        """
        Return whether DEMO order sending
        is currently enabled.

        This only reports the safety switch.
        It does not send an order.
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
    def get_history_days() -> int:
        """
        Return the number of days of MT5
        history Aladdin should load.

        Default:
            30 days

        Maximum:
            3650 days
        """

        raw_value = os.getenv(
            "ALADDIN_MT5_HISTORY_DAYS",
            "30",
        )

        try:
            days = int(raw_value)

        except ValueError:
            days = 30

        return max(
            1,
            min(
                days,
                3650,
            ),
        )

    # ======================================================
    # ACCOUNT INFORMATION
    # ======================================================

    @classmethod
    def get_account_info(cls) -> dict:
        """
        Return broker/account information.

        MOCK mode:
            No real MT5 account is accessed.

        DEMO mode:
            Connects to the active MT5 terminal
            and reads DEMO account information.

        This method is read-only.
        """

        connector = MT5Connector()

        try:
            connector.connect()

            # ==========================================
            # MOCK MODE
            # ==========================================

            if connector.mode == "MOCK":

                return {
                    "execution_mode": "MOCK",
                    "connected": True,
                    "account_connected": False,
                    "account_type": "MOCK",
                    "login": None,
                    "server": None,
                    "name": None,
                    "currency": None,
                    "balance": None,
                    "equity": None,
                    "profit": None,
                    "margin": None,
                    "free_margin": None,
                    "margin_level": None,
                    "leverage": None,
                    "trade_allowed": False,
                    "expert_trading_allowed": False,
                    "demo_execution_enabled": False,
                    "message": (
                        "Aladdin is running in MOCK mode. "
                        "No real MT5 account information "
                        "is being used."
                    ),
                }

            # ==========================================
            # DEMO MODE
            # ==========================================

            account = mt5.account_info()

            if account is None:

                raise ConnectionError(
                    "MT5 account information "
                    "is unavailable."
                )

            return {
                "execution_mode": "DEMO",
                "connected": True,
                "account_connected": True,
                "account_type": "DEMO",
                "login": int(
                    account.login
                ),
                "server": account.server,
                "name": account.name,
                "currency": account.currency,
                "balance": float(
                    account.balance
                ),
                "equity": float(
                    account.equity
                ),
                "profit": float(
                    account.profit
                ),
                "margin": float(
                    account.margin
                ),
                "free_margin": float(
                    account.margin_free
                ),
                "margin_level": float(
                    account.margin_level
                ),
                "leverage": int(
                    account.leverage
                ),
                "trade_allowed": bool(
                    account.trade_allowed
                ),
                "expert_trading_allowed": bool(
                    account.trade_expert
                ),
                "demo_execution_enabled": (
                    cls.is_demo_execution_enabled()
                ),
                "message": (
                    "Connected to MT5 DEMO account."
                ),
            }

        finally:
            connector.disconnect()

    # ======================================================
    # OPEN POSITIONS
    # ======================================================

    @classmethod
    def get_open_positions(cls) -> dict:
        """
        Return all currently open MT5 positions.

        This method only reads positions.
        It does not modify or close them.
        """

        connector = MT5Connector()

        try:
            connector.connect()

            # ==========================================
            # MOCK MODE
            # ==========================================

            if connector.mode == "MOCK":

                return {
                    "execution_mode": "MOCK",
                    "connected": True,
                    "position_count": 0,
                    "total_profit": 0.0,
                    "positions": [],
                    "message": (
                        "Aladdin is running in MOCK mode. "
                        "No real MT5 positions are loaded."
                    ),
                }

            # ==========================================
            # DEMO MODE
            # ==========================================

            positions = mt5.positions_get()

            if positions is None:

                error = mt5.last_error()

                raise ConnectionError(
                    "Unable to retrieve MT5 "
                    f"positions. Error: {error}"
                )

            position_list = []

            total_profit = 0.0

            for position in positions:

                if (
                    position.type
                    == mt5.POSITION_TYPE_BUY
                ):

                    direction = "BUY"

                elif (
                    position.type
                    == mt5.POSITION_TYPE_SELL
                ):

                    direction = "SELL"

                else:
                    direction = "UNKNOWN"

                profit = float(
                    position.profit
                )

                total_profit += profit

                identifier = getattr(
                    position,
                    "identifier",
                    position.ticket,
                )

                position_list.append(
                    {
                        "ticket": int(
                            position.ticket
                        ),
                        "identifier": int(
                            identifier
                        ),
                        "symbol": position.symbol,
                        "direction": direction,
                        "volume": float(
                            position.volume
                        ),
                        "open_price": float(
                            position.price_open
                        ),
                        "current_price": float(
                            position.price_current
                        ),
                        "stop_loss": float(
                            position.sl
                        ),
                        "take_profit": float(
                            position.tp
                        ),
                        "profit": profit,
                        "swap": float(
                            position.swap
                        ),
                        "magic": int(
                            position.magic
                        ),
                        "comment": (
                            position.comment
                            or ""
                        ),
                    }
                )

            return {
                "execution_mode": "DEMO",
                "connected": True,
                "position_count": len(
                    position_list
                ),
                "total_profit": round(
                    total_profit,
                    2,
                ),
                "positions": position_list,
                "message": (
                    "MT5 DEMO positions loaded "
                    "successfully."
                ),
            }

        finally:
            connector.disconnect()

    # ======================================================
    # COMPLETED TRADE HISTORY
    # ======================================================

    @classmethod
    def get_trade_history(
        cls,
        days: int | None = None,
    ) -> dict:
        """
        Return completed MT5 positions.

        MT5 stores activity as individual deals.

        This method:
        - Finds positions with closing activity
        - Groups all deals by position ID
        - Excludes positions that are still open
        - Includes entry and exit charges
        - Returns one record per completed position

        Reversal positions using DEAL_ENTRY_INOUT
        are currently skipped because assigning
        one BUY/SELL direction to that lifecycle
        could be misleading.

        This method is read-only.
        """

        connector = MT5Connector()

        try:
            connector.connect()

            # ==========================================
            # VALIDATE HISTORY PERIOD
            # ==========================================

            history_days = (
                days
                if days is not None
                else cls.get_history_days()
            )

            history_days = max(
                1,
                min(
                    int(history_days),
                    3650,
                ),
            )

            # ==========================================
            # MOCK MODE
            # ==========================================

            if connector.mode == "MOCK":

                return {
                    "execution_mode": "MOCK",
                    "connected": True,
                    "history_days": history_days,
                    "closed_trade_count": 0,
                    "total_profit": 0.0,
                    "total_commission": 0.0,
                    "total_swap": 0.0,
                    "total_fee": 0.0,
                    "total_net_profit": 0.0,
                    "closed_trades": [],
                    "message": (
                        "Aladdin is running in MOCK mode. "
                        "No MT5 completed-position "
                        "history is loaded."
                    ),
                }

            # ==========================================
            # HISTORY DATE RANGE
            # ==========================================

            date_to = datetime.now(
                timezone.utc
            )

            date_from = (
                date_to
                - timedelta(
                    days=history_days
                )
            )

            # ==========================================
            # LOAD DEALS INSIDE REQUESTED PERIOD
            # ==========================================

            period_deals = (
                mt5.history_deals_get(
                    date_from,
                    date_to,
                )
            )

            if period_deals is None:

                error = mt5.last_error()

                raise ConnectionError(
                    "Unable to retrieve MT5 "
                    f"trade history. Error: {error}"
                )

            # ==========================================
            # LOAD CURRENT OPEN POSITIONS
            # ==========================================

            open_positions = (
                mt5.positions_get()
            )

            if open_positions is None:

                error = mt5.last_error()

                raise ConnectionError(
                    "Unable to retrieve current MT5 "
                    f"positions. Error: {error}"
                )

            open_position_ids = set()

            for position in open_positions:

                identifier = getattr(
                    position,
                    "identifier",
                    None,
                )

                if identifier is not None:

                    open_position_ids.add(
                        int(identifier)
                    )

                # Ticket fallback.
                open_position_ids.add(
                    int(position.ticket)
                )

            # ==========================================
            # FIND POSITIONS WITH CLOSING ACTIVITY
            # ==========================================

            candidate_position_ids = set()

            for deal in period_deals:

                position_id = int(
                    getattr(
                        deal,
                        "position_id",
                        0,
                    )
                    or 0
                )

                if position_id <= 0:
                    continue

                if deal.entry in {
                    mt5.DEAL_ENTRY_OUT,
                    mt5.DEAL_ENTRY_OUT_BY,
                    mt5.DEAL_ENTRY_INOUT,
                }:

                    candidate_position_ids.add(
                        position_id
                    )

            completed_positions = []

            total_profit = 0.0
            total_commission = 0.0
            total_swap = 0.0
            total_fee = 0.0
            total_net_profit = 0.0

            # ==========================================
            # PROCESS EACH POSITION
            # ==========================================

            for position_id in sorted(
                candidate_position_ids
            ):

                # --------------------------------------
                # Still open?
                # Do not treat it as completed.
                # --------------------------------------

                if (
                    position_id
                    in open_position_ids
                ):

                    continue

                # --------------------------------------
                # Load ALL deals for position.
                #
                # This includes opening deals even if
                # they were created before date_from.
                # --------------------------------------

                position_deals = (
                    mt5.history_deals_get(
                        position=position_id
                    )
                )

                if position_deals is None:
                    continue

                position_deals = list(
                    position_deals
                )

                if not position_deals:
                    continue

                # --------------------------------------
                # Sort oldest to newest.
                # --------------------------------------

                position_deals.sort(
                    key=lambda deal: (
                        getattr(
                            deal,
                            "time_msc",
                            int(
                                deal.time
                            )
                            * 1000,
                        ),
                        int(
                            deal.ticket
                        ),
                    )
                )

                # --------------------------------------
                # Keep BUY/SELL trading deals only.
                #
                # Other MT5 deals can include balance,
                # credit, commission-only operations,
                # etc.
                # --------------------------------------

                trading_deals = [
                    deal
                    for deal in position_deals
                    if deal.type
                    in {
                        mt5.DEAL_TYPE_BUY,
                        mt5.DEAL_TYPE_SELL,
                    }
                ]

                if not trading_deals:
                    continue

                # --------------------------------------
                # Reversal protection.
                # --------------------------------------

                has_reversal = any(
                    deal.entry
                    == mt5.DEAL_ENTRY_INOUT
                    for deal in trading_deals
                )

                if has_reversal:
                    continue

                # --------------------------------------
                # Opening deals.
                # --------------------------------------

                opening_deals = [
                    deal
                    for deal in trading_deals
                    if deal.entry
                    == mt5.DEAL_ENTRY_IN
                ]

                if not opening_deals:
                    continue

                first_opening_deal = (
                    opening_deals[0]
                )

                # --------------------------------------
                # Original trade direction.
                # --------------------------------------

                if (
                    first_opening_deal.type
                    == mt5.DEAL_TYPE_BUY
                ):

                    direction = "BUY"

                elif (
                    first_opening_deal.type
                    == mt5.DEAL_TYPE_SELL
                ):

                    direction = "SELL"

                else:
                    continue

                # --------------------------------------
                # Closing deals.
                # --------------------------------------

                closing_deals = [
                    deal
                    for deal in trading_deals
                    if deal.entry
                    in {
                        mt5.DEAL_ENTRY_OUT,
                        mt5.DEAL_ENTRY_OUT_BY,
                    }
                ]

                if not closing_deals:
                    continue

                final_closing_deal = (
                    closing_deals[-1]
                )

                # --------------------------------------
                # Closed time.
                # --------------------------------------

                closed_at = (
                    datetime.fromtimestamp(
                        final_closing_deal.time,
                        tz=timezone.utc,
                    )
                )

                # --------------------------------------
                # Final close must be inside requested
                # history period.
                # --------------------------------------

                if closed_at < date_from:
                    continue

                if closed_at > date_to:
                    continue

                # --------------------------------------
                # Calculate complete financial result.
                #
                # Use ALL deals for this position so
                # entry-side commission is included.
                # --------------------------------------

                position_profit = sum(
                    float(
                        getattr(
                            deal,
                            "profit",
                            0.0,
                        )
                        or 0.0
                    )
                    for deal in position_deals
                )

                position_commission = sum(
                    float(
                        getattr(
                            deal,
                            "commission",
                            0.0,
                        )
                        or 0.0
                    )
                    for deal in position_deals
                )

                position_swap = sum(
                    float(
                        getattr(
                            deal,
                            "swap",
                            0.0,
                        )
                        or 0.0
                    )
                    for deal in position_deals
                )

                position_fee = sum(
                    float(
                        getattr(
                            deal,
                            "fee",
                            0.0,
                        )
                        or 0.0
                    )
                    for deal in position_deals
                )

                net_profit = (
                    position_profit
                    + position_commission
                    + position_swap
                    + position_fee
                )

                # --------------------------------------
                # Opened volume.
                # --------------------------------------

                opened_volume = sum(
                    float(
                        deal.volume
                    )
                    for deal in opening_deals
                )

                # --------------------------------------
                # Identify Aladdin trades.
                #
                # Check all deals because the comment
                # or magic may be missing from an exit.
                # --------------------------------------

                is_aladdin_trade = any(
                    (
                        int(
                            getattr(
                                deal,
                                "magic",
                                0,
                            )
                            or 0
                        )
                        == 20260911
                    )
                    or (
                        "ALADDIN"
                        in (
                            getattr(
                                deal,
                                "comment",
                                "",
                            )
                            or ""
                        ).upper()
                    )
                    for deal in position_deals
                )

                # --------------------------------------
                # Prefer opening comment.
                # --------------------------------------

                comment = (
                    getattr(
                        first_opening_deal,
                        "comment",
                        "",
                    )
                    or ""
                )

                # --------------------------------------
                # Determine magic number.
                # --------------------------------------

                magic = int(
                    getattr(
                        first_opening_deal,
                        "magic",
                        0,
                    )
                    or 0
                )

                # --------------------------------------
                # Determine symbol.
                # --------------------------------------

                symbol = (
                    getattr(
                        first_opening_deal,
                        "symbol",
                        "",
                    )
                    or getattr(
                        final_closing_deal,
                        "symbol",
                        "",
                    )
                    or ""
                )

                if not symbol:
                    continue

                # --------------------------------------
                # One completed position record.
                #
                # Final closing deal ticket acts as the
                # unique completed-trade identifier.
                # --------------------------------------

                trade_record = {
                    "deal_ticket": int(
                        final_closing_deal.ticket
                    ),
                    "order_ticket": int(
                        final_closing_deal.order
                    ),
                    "position_id": int(
                        position_id
                    ),
                    "symbol": symbol,
                    "direction": direction,
                    "volume": round(
                        opened_volume,
                        8,
                    ),
                    "close_price": float(
                        final_closing_deal.price
                    ),
                    "profit": round(
                        position_profit,
                        2,
                    ),
                    "commission": round(
                        position_commission,
                        2,
                    ),
                    "swap": round(
                        position_swap,
                        2,
                    ),
                    "fee": round(
                        position_fee,
                        2,
                    ),
                    "net_profit": round(
                        net_profit,
                        2,
                    ),
                    "time": (
                        closed_at.isoformat()
                    ),
                    "magic": magic,
                    "comment": comment,
                    "is_aladdin_trade": (
                        is_aladdin_trade
                    ),
                }

                completed_positions.append(
                    trade_record
                )

                total_profit += (
                    position_profit
                )

                total_commission += (
                    position_commission
                )

                total_swap += (
                    position_swap
                )

                total_fee += (
                    position_fee
                )

                total_net_profit += (
                    net_profit
                )

            # ==========================================
            # NEWEST COMPLETED POSITION FIRST
            # ==========================================

            completed_positions.sort(
                key=lambda trade: (
                    trade["time"]
                ),
                reverse=True,
            )

            return {
                "execution_mode": "DEMO",
                "connected": True,
                "history_days": (
                    history_days
                ),
                "closed_trade_count": len(
                    completed_positions
                ),
                "total_profit": round(
                    total_profit,
                    2,
                ),
                "total_commission": round(
                    total_commission,
                    2,
                ),
                "total_swap": round(
                    total_swap,
                    2,
                ),
                "total_fee": round(
                    total_fee,
                    2,
                ),
                "total_net_profit": round(
                    total_net_profit,
                    2,
                ),
                "closed_trades": (
                    completed_positions
                ),
                "message": (
                    "MT5 DEMO completed-position "
                    "history loaded successfully."
                ),
            }

        finally:
            connector.disconnect()

    # ======================================================
    # COMPLETE BROKER STATUS
    # ======================================================

    @classmethod
    def get_broker_status(cls) -> dict:
        """
        Return a combined broker overview.

        Includes:
        - Account information
        - Open positions

        Trade history is intentionally not
        included here because broker status
        may be refreshed frequently.

        This remains completely read-only.
        """

        account = (
            cls.get_account_info()
        )

        positions = (
            cls.get_open_positions()
        )

        return {
            "execution_mode": (
                account[
                    "execution_mode"
                ]
            ),
            "account": account,
            "position_count": (
                positions[
                    "position_count"
                ]
            ),
            "total_open_profit": (
                positions[
                    "total_profit"
                ]
            ),
            "positions": (
                positions[
                    "positions"
                ]
            ),
        }