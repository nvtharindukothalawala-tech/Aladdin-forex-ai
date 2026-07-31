"""
repository.py

Database operations for trades.

Author: Tharindu Kothalwala
Project: Aladdin
"""

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

    def save_trade(
        self,
        trade,
        user_id: int = 1,
    ):
        """
        Save a trade into database.

        user_id has a default value for
        backward compatibility with old tests.
        """

        db_trade = TradeModel(
            user_id=user_id,
            symbol=trade.symbol,
            direction=trade.direction,
            result=trade.result,
            profit_loss=trade.profit_loss,
            risk_reward=trade.risk_reward,
        )

        self.session.add(db_trade)

        self.session.commit()

        self.session.refresh(db_trade)

        return db_trade

    def get_user_trades(
        self,
        user_id: int,
    ):
        """
        Return trades belonging to a user.
        """

        return (
            self.session.query(TradeModel).filter(TradeModel.user_id == user_id).all()
        )

    def count_user_trades(
        self,
        user_id: int,
    ):
        """
        Return trade count for a user.
        """

        return (
            self.session.query(TradeModel).filter(TradeModel.user_id == user_id).count()
        )

    def get_all_trades(self):
        """
        Return all trades.

        Kept for backward compatibility.
        """

        return self.session.query(TradeModel).all()

    def count_trades(self):
        """
        Return total trade count.

        Kept for backward compatibility.
        """

        return self.session.query(TradeModel).count()
