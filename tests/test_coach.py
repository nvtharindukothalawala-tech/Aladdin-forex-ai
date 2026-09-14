"""
test_coach.py

Tests AI coaching engine.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from app.coaching.coach import AICoach


def test_positive_trading_report():
    """
    Test coaching feedback for positive
    journal performance.
    """

    report = AICoach.generate_report(
        win_rate=70,
        average_risk_reward=2.5,
        total_profit=1000,
    )

    assert (
        report.summary
        == (
            "Current journal performance is positive, "
            "but results should continue to be evaluated "
            "across more completed trades."
        )
    )

    assert (
        "The current journal shows a strong win rate."
        in report.strengths
    )

    assert (
        "The recorded trades show an average risk/reward ratio of at least 1:2."
        in report.strengths
    )

    assert (
        "The journal currently shows positive net performance."
        in report.strengths
    )

    assert report.weaknesses == []

    assert len(report.recommendations) > 0


def test_negative_trading_report():
    """
    Test coaching feedback for negative
    journal performance.
    """

    report = AICoach.generate_report(
        win_rate=40,
        average_risk_reward=1,
        total_profit=-200,
    )

    assert (
        report.summary
        == (
            "Current journal performance is negative "
            "and shows areas that should be reviewed."
        )
    )

    assert (
        "The current journal shows a low win rate."
        in report.weaknesses
    )

    assert (
        "The average recorded risk/reward ratio is below 1:2."
        in report.weaknesses
    )

    assert (
        "The journal currently shows negative net performance."
        in report.weaknesses
    )

    assert (
        "Review losing trades to identify repeated setup "
        "or execution mistakes."
        in report.recommendations
    )

    assert (
        "Review lower risk/reward setups and compare them "
        "with better-performing trades."
        in report.recommendations
    )


def test_no_completed_trades_report():
    """
    Test that the coach does not judge performance
    when there are no completed journal trades.
    """

    report = AICoach.generate_report(
        win_rate=0,
        average_risk_reward=0,
        total_profit=0,
        trade_count=0,
        risk_reward_trade_count=0,
    )

    assert (
        report.summary
        == (
            "Not enough completed trade data is "
            "available for coaching yet."
        )
    )

    assert report.strengths == []

    assert report.weaknesses == []

    assert (
        "Complete and journal more trades before "
        "evaluating trading performance."
        in report.recommendations
    )


def test_small_sample_does_not_judge_performance():
    """
    Test that the coach avoids drawing performance
    conclusions from fewer than five completed trades.
    """

    report = AICoach.generate_report(
        win_rate=0,
        average_risk_reward=0,
        total_profit=-2,
        trade_count=1,
        risk_reward_trade_count=0,
    )

    assert (
        report.summary
        == (
            "Only 1 completed trade is available. "
            "This sample is too small for reliable "
            "performance-pattern coaching."
        )
    )

    assert report.strengths == []

    assert report.weaknesses == []

    assert (
        "Complete at least 5 journaled trades before "
        "using win rate or total profit to identify "
        "performance patterns."
        in report.recommendations
    )

    assert (
        "Risk/reward performance cannot be evaluated yet "
        "because the available trades do not contain "
        "risk/reward data."
        in report.recommendations
    )

    assert (
        "The current journal shows a low win rate."
        not in report.weaknesses
    )

    assert (
        "The journal currently shows negative net performance."
        not in report.weaknesses
    )


def test_four_trades_still_use_small_sample_protection():
    """
    Test the upper boundary of the small-sample rule.
    Four completed trades must still avoid performance
    conclusions.
    """

    report = AICoach.generate_report(
        win_rate=25,
        average_risk_reward=0,
        total_profit=-10,
        trade_count=4,
        risk_reward_trade_count=0,
    )

    assert (
        report.summary
        == (
            "Only 4 completed trades are available. "
            "This sample is too small for reliable "
            "performance-pattern coaching."
        )
    )

    assert report.strengths == []
    assert report.weaknesses == []

    assert (
        "Complete at least 5 journaled trades before "
        "using win rate or total profit to identify "
        "performance patterns."
        in report.recommendations
    )

    assert (
        "The current journal shows a low win rate."
        not in report.weaknesses
    )

    assert (
        "The journal currently shows negative net performance."
        not in report.weaknesses
    )


def test_five_trades_enable_normal_performance_analysis():
    """
    Test that the minimum sample threshold is inclusive.
    At five completed trades, normal coaching analysis
    should begin.
    """

    report = AICoach.generate_report(
        win_rate=40,
        average_risk_reward=1,
        total_profit=-100,
        trade_count=5,
        risk_reward_trade_count=5,
    )

    assert (
        report.summary
        == (
            "Current journal performance is negative "
            "and shows areas that should be reviewed."
        )
    )

    assert (
        "The current journal shows a low win rate."
        in report.weaknesses
    )

    assert (
        "The average recorded risk/reward ratio is below 1:2."
        in report.weaknesses
    )

    assert (
        "The journal currently shows negative net performance."
        in report.weaknesses
    )

    assert (
        "Complete at least 5 journaled trades before "
        "using win rate or total profit to identify "
        "performance patterns."
        not in report.recommendations
    )
