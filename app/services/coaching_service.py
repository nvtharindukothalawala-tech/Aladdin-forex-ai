"""
coaching_service.py

Business logic for AI coaching.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.analytics.performance_analyzer import (
    PerformanceAnalyzer,
)

from app.coaching.coach import (
    AICoach,
)


class CoachingService:
    """
    Generates trader coaching reports.
    """

    def __init__(
        self,
        repository,
    ):

        self.repository = repository

    def generate_report(self):

        trades = self.repository.get_all_trades()

        analyzer = PerformanceAnalyzer(trades)

        report = AICoach.generate_report(
            win_rate=analyzer.win_rate(),
            average_risk_reward=(analyzer.average_risk_reward()),
            total_profit=(analyzer.total_profit()),
        )

        return report
