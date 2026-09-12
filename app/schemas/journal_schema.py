"""
journal_schema.py

Schemas for journal API responses.

Supports:
- Normal Aladdin journal trades
- Imported MT5 completed trades

Author: Tharindu Kothalawala
Project: Aladdin
"""

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


class JournalTradeResponse(BaseModel):
    """
    Response schema for journal trades.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    # ==================================================
    # BASIC TRADE INFORMATION
    # ==================================================

    symbol: str

    direction: str

    result: str

    profit_loss: float

    # MT5-imported trades may not have a reliable
    # original risk/reward value.
    risk_reward: float | None = None

    # ==================================================
    # TRADE SOURCE
    # ==================================================

    source: str | None = None

    # ==================================================
    # MT5 IDENTIFIERS
    # ==================================================

    mt5_deal_ticket: int | None = None

    mt5_order_ticket: int | None = None

    mt5_position_id: int | None = None

    # ==================================================
    # MT5 FINANCIAL INFORMATION
    # ==================================================

    close_price: float | None = None

    commission: float | None = None

    swap: float | None = None

    fee: float | None = None

    # ==================================================
    # MT5 TRADE INFORMATION
    # ==================================================

    closed_at: datetime | None = None

    is_aladdin_trade: int | None = None