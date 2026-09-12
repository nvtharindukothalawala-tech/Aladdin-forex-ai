"""
coach.py

Generates trading improvement suggestions
from performance statistics.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from dataclasses import dataclass


@dataclass
class CoachingReport:
    """
    Stores AI coaching output.
    """

    summary: str

    strengths: list[str]

    weaknesses: list[str]

    recommendations: list[str]


class AICoach:
    """
    Provides trading performance feedback.

    The coach uses performance statistics from
    the user's trade journal.

    It does not make guaranteed-profit claims
    or automatically execute trades.
    """

    @staticmethod
    def generate_report(
        win_rate: float,
        average_risk_reward: float,
        total_profit: float,
        trade_count: int | None = None,
        risk_reward_trade_count: int | None = None,
    ) -> CoachingReport:
        """
        Generate coaching feedback.

        Parameters
        ----------
        win_rate:
            Percentage of winning trades.

        average_risk_reward:
            Average risk/reward value calculated only
            from trades that have risk/reward data.

        total_profit:
            Total journal profit or loss.

        trade_count:
            Number of trades available for analysis.

        risk_reward_trade_count:
            Number of trades that contain valid
            risk/reward information.
        """

        strengths: list[str] = []

        weaknesses: list[str] = []

        recommendations: list[str] = []

        # -------------------------------------------------
        # NO TRADE DATA
        # -------------------------------------------------

        if trade_count is not None and trade_count <= 0:

            return CoachingReport(
                summary=(
                    "Not enough completed trade data is "
                    "available for coaching yet."
                ),
                strengths=[],
                weaknesses=[],
                recommendations=[
                    (
                        "Complete and journal more trades "
                        "before evaluating trading performance."
                    )
                ],
            )

        # -------------------------------------------------
        # WIN RATE ANALYSIS
        # -------------------------------------------------

        if win_rate >= 60:

            strengths.append(
                "The current journal shows a strong win rate."
            )

        elif win_rate >= 45:

            recommendations.append(
                (
                    "Review both winning and losing trades "
                    "to identify patterns that may improve "
                    "trade consistency."
                )
            )

        else:

            weaknesses.append(
                "The current journal shows a low win rate."
            )

            recommendations.append(
                (
                    "Review losing trades to identify "
                    "repeated setup or execution mistakes."
                )
            )

        # -------------------------------------------------
        # RISK / REWARD ANALYSIS
        # -------------------------------------------------

        if (
            risk_reward_trade_count is not None
            and risk_reward_trade_count <= 0
        ):

            recommendations.append(
                (
                    "Risk/reward performance cannot be "
                    "evaluated yet because the available "
                    "trades do not contain risk/reward data."
                )
            )

        elif average_risk_reward >= 2:

            strengths.append(
                (
                    "The recorded trades show an average "
                    "risk/reward ratio of at least 1:2."
                )
            )

        elif average_risk_reward > 0:

            weaknesses.append(
                (
                    "The average recorded risk/reward ratio "
                    "is below 1:2."
                )
            )

            recommendations.append(
                (
                    "Review lower risk/reward setups and "
                    "compare them with better-performing trades."
                )
            )

        else:

            recommendations.append(
                (
                    "More valid risk/reward data is needed "
                    "before evaluating risk/reward performance."
                )
            )

        # -------------------------------------------------
        # PROFIT ANALYSIS
        # -------------------------------------------------

        if total_profit > 0:

            strengths.append(
                "The journal currently shows positive net performance."
            )

            summary = (
                "Current journal performance is positive, "
                "but results should continue to be evaluated "
                "across more completed trades."
            )

        elif total_profit < 0:

            weaknesses.append(
                "The journal currently shows negative net performance."
            )

            recommendations.append(
                (
                    "Review the largest losing trades and "
                    "look for repeated risk or execution patterns."
                )
            )

            summary = (
                "Current journal performance is negative and "
                "shows areas that should be reviewed."
            )

        else:

            summary = (
                "Current journal performance is approximately "
                "breakeven."
            )

        # -------------------------------------------------
        # FALLBACK
        # -------------------------------------------------

        if not recommendations:

            recommendations.append(
                (
                    "Continue recording completed trades so "
                    "Aladdin can evaluate performance over "
                    "a larger sample."
                )
            )

        return CoachingReport(
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
        )