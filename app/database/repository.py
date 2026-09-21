"""
repository.py

Database operations for trades.

This repository uses SQLAlchemy database storage.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from datetime import datetime

from sqlalchemy.exc import IntegrityError

from app.database.models import TradeModel


class TradeRepository:
    """
    Handles trade database operations.
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

        This keeps the previous behavior for
        backward compatibility.
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
        Find an imported MT5 trade using
        its unique MT5 deal ticket.
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
        Return True if an MT5 deal has already
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
        Import one MT5 closed trade into
        the Aladdin journal.

        Duplicate MT5 deal tickets are ignored.

        profit_loss uses net broker P/L:

            profit
            + commission
            + swap
            + fee

        risk_reward may be None when the
        original planned R:R is unavailable.
        """

        # ----------------------------------------------
        # Validate required values
        # ----------------------------------------------

        if deal_ticket is None:
            raise ValueError(
                "MT5 deal ticket is required."
            )

        if not symbol:
            raise ValueError(
                "Trade symbol is required."
            )

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
        # Calculate true journal P/L
        # ----------------------------------------------

        net_profit = (
            float(profit)
            + float(commission or 0.0)
            + float(swap or 0.0)
            + float(fee or 0.0)
        )

        # ----------------------------------------------
        # Determine trade result
        # ----------------------------------------------

        if net_profit > 0:
            result = "WIN"

        elif net_profit < 0:
            result = "LOSS"

        else:
            result = "BREAKEVEN"

        # ----------------------------------------------
        # Build database record
        # ----------------------------------------------

        db_trade = TradeModel(
            user_id=user_id,
            symbol=symbol,
            direction=normalized_direction,
            result=result,
            profit_loss=net_profit,
            risk_reward=risk_reward,
            source="MT5",
            mt5_deal_ticket=deal_ticket,
            mt5_order_ticket=order_ticket,
            mt5_position_id=position_id,
            close_price=close_price,
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
        # Save safely
        # ----------------------------------------------

        try:
            self.session.add(db_trade)
            self.session.commit()
            self.session.refresh(db_trade)

            return db_trade, True

        except IntegrityError:
            """
            Handles race conditions where two
            requests try to import the same MT5
            deal at the same time.
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
    # JOURNAL READ OPERATIONS
    # ==================================================

    def get_user_trades(
        self,
        user_id: int,
    ):
        """
        Return trades belonging to a user.
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
        Return trade count for a user.
        """

        return (
            self.session.query(TradeModel)
            .filter(
                TradeModel.user_id
                == user_id
            )
            .count()
        )

    def get_all_trades(self):
        """
        Return all trades.

        Kept for backward compatibility.
        """

        return (
            self.session.query(
                TradeModel
            )
            .all()
        )

    def count_trades(self):
        """
        Return total trade count.

        Kept for backward compatibility.
        """

        return (
            self.session.query(
                TradeModel
            )
            .count()
        )