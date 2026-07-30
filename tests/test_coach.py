"""
test_coach.py

Tests AI coaching engine.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.coaching.coach import AICoach


def test_positive_trading_report():

    report = AICoach.generate_report(
        win_rate=70,
        average_risk_reward=2.5,
        total_profit=1000,
    )

    assert report.summary == "Trading performance is positive."

    assert "Good trade accuracy." in report.strengths

    assert "Good risk reward management." in report.strengths


def test_negative_trading_report():

    report = AICoach.generate_report(
        win_rate=40,
        average_risk_reward=1,
        total_profit=-200,
    )

    assert "Low win rate needs improvement." in report.weaknesses

    assert "Avoid trades below 1:2 risk reward." in report.recommendations
