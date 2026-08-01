"""
test_ai_coach.py

Tests AI coaching layer.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.analytics.performance_analyzer import (
    PerformanceAnalyzer,
)


from app.journal.trade_journal import (
    JournalTrade,
)


from app.journal.ai_coach import (
    AICoach,
)


def test_ai_coaching_feedback():

    trades = [
        JournalTrade(
            symbol="EUR/USD",
            direction="BUY",
            result="WIN",
            profit_loss=100,
            risk_reward=2,
        ),
        JournalTrade(
            symbol="GBP/USD",
            direction="SELL",
            result="LOSS",
            profit_loss=-50,
            risk_reward=2,
        ),
    ]

    analyzer = PerformanceAnalyzer(trades)

    feedback = AICoach.generate_feedback(analyzer)

    assert "win rate needs improvement" in feedback

    assert "risk-reward" in feedback

    assert "profitable" in feedback
