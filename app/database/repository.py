"""
repository.py

SQLAlchemy database repository for journal trades.

This repository is used by database-backed journal,
performance, coaching, and MT5 synchronization services.

The JSON-based TradeRepository remains separately in:

    app.repositories.trade_repository

Author: Tharindu Kothalawala
Project: Aladdin
"""

from datetime import datetime

from sqlalchemy.exc import IntegrityError

from app.database.models import TradeModel


class TradeRepository:
    """
    Handles database-backed trade operations.

    This repository uses a SQLAlchemy Session.

    It is intentionally separate from the JSON repository
    located at app.repositories.trade_repository.
    """

    def __init__(
        self,
        session,
    ):
        self.session = session

    # ==================================================
    # EXISTING JOURNAL SAVE
    # ==================================================

    def save_trade(
        self,
        trade,
        user_id: int = 1,
    ):
        """
        Save a normal Aladdin journal trade.

        The default user_id=1 is retained for backward
        compatibility with existing tests and callers.
        """

        db_trade = TradeModel(
            user_id=user_id,
            symbol=trade.symbol,
            direction=trade.direction,
            result=trade.result,
            profit_loss=trade.profit_loss,
            risk_reward=trade.risk_reward,
        )

        try:
            self.session.add(db_trade)
            self.session.commit()
            self.session.refresh(db_trade)

            return db_trade

        except Exception:
            self.session.rollback()
            raise

    # ==================================================
    # MT5 DUPLICATE LOOKUP
    # ==================================================

    def get_by_mt5_deal_ticket(
        self,
        mt5_deal_ticket: int,
    ):
        """
        Find an imported MT5 trade using its
        unique MT5 closing deal ticket.
        """

        return (
            self.session.query(TradeModel)
            .filter(
                TradeModel.mt5_deal_ticket
                == mt5_deal_ticket
            )
            .first()
        )

    def mt5_deal_exists(
        self,
        mt5_deal_ticket: int,
    ) -> bool:
        """
        Return True when an MT5 deal has already
        been imported into the journal.
        """

        return (
            self.get_by_mt5_deal_ticket(
                mt5_deal_ticket
            )
            is not None
        )

    # ==================================================
    # MT5 JOURNAL IMPORT
    # ==================================================

    def save_mt5_closed_trade(
        self,
        *,
        user_id: int,
        deal_ticket: int,
        order_ticket: int | None,
        position_id: int | None,
        symbol: str,
        direction: str,
        close_price: float,
        profit: float,
        commission: float = 0.0,
        swap: float = 0.0,
        fee: float = 0.0,
        closed_at: datetime | None = None,
        is_aladdin_trade: bool = False,
        risk_reward: float | None = None,
    ):
        """
        Import one completed MT5 trade into
        the Aladdin journal.

        Duplicate MT5 closing deal tickets are
        ignored.

        Net P/L is calculated as:

            profit
            + commission
            + swap
            + fee

        Returns:
            tuple:
                (TradeModel, created)

                created=True
                    A new database row was created.

                created=False
                    The MT5 deal already existed.
        """

        # ----------------------------------------------
        # Validate deal ticket
        # ----------------------------------------------

        if deal_ticket is None:
            raise ValueError(
                "MT5 deal ticket is required."
            )

        # ----------------------------------------------
        # Validate symbol
        # ----------------------------------------------

        normalized_symbol = (
            str(symbol)
            .strip()
            .upper()
        )

        if not normalized_symbol:
            raise ValueError(
                "Trade symbol is required."
            )

        # ----------------------------------------------
        # Validate direction
        # ----------------------------------------------

        normalized_direction = (
            str(direction)
            .strip()
            .upper()
        )

        if normalized_direction not in {
            "BUY",
            "SELL",
        }:
            raise ValueError(
                "MT5 trade direction must be "
                "BUY or SELL."
            )

        # ----------------------------------------------
        # Prevent duplicate imports
        # ----------------------------------------------

        existing_trade = (
            self.get_by_mt5_deal_ticket(
                deal_ticket
            )
        )

        if existing_trade is not None:
            return existing_trade, False

        # ----------------------------------------------
        # Calculate net broker P/L
        # ----------------------------------------------

        net_profit = (
            float(profit or 0.0)
            + float(commission or 0.0)
            + float(swap or 0.0)
            + float(fee or 0.0)
        )

        # ----------------------------------------------
        # Determine journal result
        # ----------------------------------------------

        if net_profit > 0:
            result = "WIN"

        elif net_profit < 0:
            result = "LOSS"

        else:
            result = "BREAKEVEN"

        # ----------------------------------------------
        # Create database model
        # ----------------------------------------------

        db_trade = TradeModel(
            user_id=user_id,
            symbol=normalized_symbol,
            direction=normalized_direction,
            result=result,
            profit_loss=net_profit,
            risk_reward=risk_reward,
            source="MT5",
            mt5_deal_ticket=int(
                deal_ticket
            ),
            mt5_order_ticket=(
                int(order_ticket)
                if order_ticket is not None
                else None
            ),
            mt5_position_id=(
                int(position_id)
                if position_id is not None
                else None
            ),
            close_price=float(
                close_price or 0.0
            ),
            commission=float(
                commission or 0.0
            ),
            swap=float(
                swap or 0.0
            ),
            fee=float(
                fee or 0.0
            ),
            closed_at=closed_at,
            is_aladdin_trade=(
                1
                if is_aladdin_trade
                else 0
            ),
        )

        # ----------------------------------------------
        # Persist safely
        # ----------------------------------------------

        try:
            self.session.add(db_trade)
            self.session.commit()
            self.session.refresh(db_trade)

            return db_trade, True

        except IntegrityError:
            """
            Handle a race where two requests attempt
            to import the same MT5 deal simultaneously.
            """

            self.session.rollback()

            existing_trade = (
                self.get_by_mt5_deal_ticket(
                    deal_ticket
                )
            )

            if existing_trade is not None:
                return existing_trade, False

            raise

        except Exception:
            self.session.rollback()
            raise

    # ==================================================
    # USER JOURNAL READ OPERATIONS
    # ==================================================

    def get_user_trades(
        self,
        user_id: int,
    ):
        """
        Return all journal trades belonging
        to one user.
        """

        return (
            self.session.query(TradeModel)
            .filter(
                TradeModel.user_id
                == user_id
            )
            .all()
        )

    def count_user_trades(
        self,
        user_id: int,
    ):
        """
        Return the number of journal trades
        belonging to one user.
        """

        return (
            self.session.query(TradeModel)
            .filter(
                TradeModel.user_id
                == user_id
            )
            .count()
        )

    # ==================================================
    # LEGACY READ OPERATIONS
    # ==================================================

    def get_all_trades(self):
        """
        Return every journal trade.

        Retained for backward compatibility.
        """

        return (
            self.session.query(
                TradeModel
            )
            .all()
        )

    def count_trades(self):
        """
        Return total journal trade count.

        Retained for backward compatibility.
        """

        return (
            self.session.query(
                TradeModel
            )
            .count()
        )