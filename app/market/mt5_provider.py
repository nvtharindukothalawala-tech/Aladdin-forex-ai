"""
mt5_provider.py

Provides real Forex market data from MetaTrader 5
for the Aladdin Forex Trading Assistant.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from datetime import datetime, timezone

import MetaTrader5 as mt5

from app.market.candle import Candle


class MT5DataProvider:
    """
    Get Forex market candle data from MetaTrader 5.
    """

    def __init__(self):
        """
        Create the MT5 data provider.
        """

        self.connected = False

    def connect(self):
        """
        Connect Python to the MetaTrader 5 terminal.
        """

        if self.connected:
            return True

        if not mt5.initialize():
            error = mt5.last_error()

            raise RuntimeError(
                f"Unable to connect to MetaTrader 5: {error}"
            )

        self.connected = True

        return True

    def disconnect(self):
        """
        Disconnect from MetaTrader 5.
        """

        if self.connected:
            mt5.shutdown()

            self.connected = False

    def get_candles(
        self,
        symbol,
        timeframe,
        count=100,
    ):
        """
        Get recent candles from MetaTrader 5.

        Args:
            symbol:
                MT5 symbol, for example EURUSD.

            timeframe:
                MT5 timeframe constant.

            count:
                Number of candles to retrieve.

        Returns:
            List of Candle objects.
        """

        self.connect()

        rates = mt5.copy_rates_from_pos(
            symbol,
            timeframe,
            0,
            count,
        )

        if rates is None:
            error = mt5.last_error()

            raise RuntimeError(
                f"Unable to retrieve market data: {error}"
            )

        candles = []

        for rate in rates:

            timestamp = datetime.fromtimestamp(
                int(rate["time"]),
                tz=timezone.utc,
            )

            candle = Candle(
                symbol=symbol,
                timeframe=str(timeframe),
                open_price=float(rate["open"]),
                high_price=float(rate["high"]),
                low_price=float(rate["low"]),
                close_price=float(rate["close"]),
                volume=float(rate["tick_volume"]),
                timestamp=timestamp,
            )

            candles.append(candle)

        return candles