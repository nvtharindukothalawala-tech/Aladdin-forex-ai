"""
datetime_utils.py

Contains reusable date and time helper functions
for the Aladdin Forex Trading Assistant.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from datetime import datetime


def get_current_datetime():
    """
    Return the current date and time.

    Returns:
        datetime:
            Current system date and time.
    """

    return datetime.now()


def format_datetime(value):
    """
    Convert datetime object into readable string format.

    Args:
        value:
            datetime object.

    Returns:
        str:
            Formatted date and time.
    """

    return value.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
