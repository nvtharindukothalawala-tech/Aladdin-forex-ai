"""
coach.py

Generates trading improvement suggestions
from performance statistics.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from dataclasses import dataclass


@dataclass
class CoachingReport:
    """
    Stores AI coaching output.
    """

    summary: str

    strengths: list

    weaknesses: list

    recommendations: list


class AICoach:
    """
    Provides trading performance feedback.
    """

    @staticmethod
    def generate_report(
        win_rate,
        average_risk_reward,
        total_profit,
    ):
        """
        Generate coaching feedback.
        """

        strengths = []

        weaknesses = []

        recommendations = []

        # Analyze win rate

        if win_rate >= 60:

            strengths.append("Good trade accuracy.")

        else:

            weaknesses.append("Low win rate needs improvement.")

            recommendations.append("Review losing trades.")

        # Analyze risk reward

        if average_risk_reward >= 2:

            strengths.append("Good risk reward management.")

        else:

            weaknesses.append("Risk reward is below target.")

            recommendations.append("Avoid trades below 1:2 risk reward.")

        # Analyze profit

        if total_profit > 0:

            summary = "Trading performance is positive."

        else:

            summary = "Trading performance requires improvement."

        return CoachingReport(
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
        )
