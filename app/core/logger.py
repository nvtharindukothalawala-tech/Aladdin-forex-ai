"""
logger.py

Contains logging configuration
for the Aladdin Forex Trading Assistant.

Author: Tharindu Kothalwala
Project: Aladdin
"""

import logging


def get_logger(name):
    """
    Create and return a logger object.

    Args:
        name: Name of the module using the logger.

    Returns:
        Logger object.
    """

    logger = logging.getLogger(name)

    # Set logging level
    logger.setLevel(logging.INFO)

    # Create console output
    handler = logging.StreamHandler()

    # Define message format
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    handler.setFormatter(formatter)

    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
