"""
test_performance_analyzer.py

Tests performance analytics.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.analytics.performance_analyzer import (
    PerformanceAnalyzer,
)

from app.journal.trade_journal import (
    JournalTrade,
)


def test_performance_statistics():

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
            risk_reward=1,
        ),
    ]

    analyzer = PerformanceAnalyzer(trades)

    assert analyzer.total_trades() == 2

    assert analyzer.winning_trades() == 1

    assert analyzer.losing_trades() == 1

    assert analyzer.win_rate() == 50

    assert analyzer.total_profit() == 50

    assert analyzer.average_risk_reward() == 1.5
