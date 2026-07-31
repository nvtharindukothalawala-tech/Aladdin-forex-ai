"""
journal_service.py

Handles journal business logic.

Author: Tharindu Kothalwala
Project: Aladdin
"""


class JournalService:
    """
    Provides journal operations.
    """


    def __init__(
        self,
        repository,
    ):

        self.repository = repository



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