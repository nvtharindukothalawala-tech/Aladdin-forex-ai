"""
ai_coach.py

Generates trading advice from performance data.

Author: Tharindu Kothalwala
Project: Aladdin
"""


class AICoach:
    """
    Provides AI trading feedback
    based on historical performance.
    """

    @staticmethod
    def generate_feedback(
        performance_analyzer,
    ):
        """
        Generate coaching message.
        """

        total_trades = performance_analyzer.total_trades()

        if total_trades == 0:

            return "Not enough trading data " "available for analysis."

        win_rate = performance_analyzer.win_rate()

        average_rr = performance_analyzer.average_risk_reward()

        total_profit = performance_analyzer.total_profit()

        feedback = []

        if win_rate >= 60:

            feedback.append("Your trading strategy shows " "good consistency.")

        else:

            feedback.append("Your win rate needs improvement.")

        if average_rr >= 2:

            feedback.append("Your risk-reward management " "is strong.")

        else:

            feedback.append("Consider improving risk-reward ratio.")

        if total_profit > 0:

            feedback.append("Your overall trading performance " "is profitable.")

        else:

            feedback.append("Review losing trades and improve entries.")

        return " ".join(feedback)
