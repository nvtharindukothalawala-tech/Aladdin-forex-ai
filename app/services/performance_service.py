"""
performance_service.py

Business logic for performance analytics.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.analytics.performance_analyzer import (
    PerformanceAnalyzer,
)


class PerformanceService:
    """
    Provides trading performance information.
    """

    def __init__(
        self,
        repository,
    ):

        self.repository = repository

    def get_performance(
        self,
        user_id: int,
    ):
        """
        Generate performance report
        for a specific user.
        """

        trades = self.repository.get_user_trades(user_id)

        analyzer = PerformanceAnalyzer(trades)

        return {
            "total_trades": analyzer.total_trades(),
            "winning_trades": analyzer.winning_trades(),
            "losing_trades": analyzer.losing_trades(),
            "win_rate": analyzer.win_rate(),
            "total_profit": analyzer.total_profit(),
            "average_risk_reward": analyzer.average_risk_reward(),
        }
