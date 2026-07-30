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

    def __init__(self, session):

        self.session = session

    def save_trade(
        self,
        trade,
    ):
        """
        Save a trade into database.
        """

        db_trade = TradeModel(
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

    def get_all_trades(self):
        """
        Return all trades.
        """

        return self.session.query(TradeModel).all()

    def count_trades(self):
        """
        Return trade count.
        """

        return self.session.query(TradeModel).count()
