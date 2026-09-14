"""
mt5_session.py

Provides process-level synchronization for
MetaTrader 5 Python access in the Aladdin project.

The MetaTrader5 Python package maintains global
connection state inside the Python process.

Concurrent FastAPI requests must therefore not
initialize, use, or shut down MT5 at the same time.

The shared lock protects the complete MT5 session
lifetime from connect() until disconnect().

Author: Tharindu Kothalawala
Project: Aladdin
"""

from threading import Lock


# ==========================================================
# SHARED MT5 SESSION LOCK
# ==========================================================

MT5_SESSION_LOCK = Lock()