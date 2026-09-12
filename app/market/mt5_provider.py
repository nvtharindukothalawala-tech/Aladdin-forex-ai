"""
mt5_provider.py

Provides real Forex market data from MetaTrader 5
for the Aladdin Forex Trading Assistant.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from datetime import datetime, timezone

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

from app.market.candle import Candle
from app.market.mt5_symbol_resolver import (
    MT5SymbolResolver,
)


class MT5DataProvider:
    """
    Get Forex market candle data from MetaTrader 5.

    MetaTrader5 is an optional dependency so that
    Aladdin can still be imported and tested on
    non-Windows environments such as GitHub Actions.

    Real MT5 market data requires Windows with the
    MetaTrader5 Python package installed.
    """

    def __init__(self):
        """
        Create the MT5 data provider.
        """

        self.connected = False

    # ======================================================
    # MT5 AVAILABILITY
    # ======================================================

    @staticmethod
    def _require_mt5():
        """
        Ensure the MetaTrader5 package is available.
        """

        if mt5 is None:
            raise RuntimeError(
                "MetaTrader5 is not installed on this platform. "
                "Real MT5 market data requires Windows with the "
                "MetaTrader5 Python package installed."
            )

        return mt5

    # ======================================================
    # CONNECTION
    # ======================================================

    def connect(self):
        """
        Connect Python to the MetaTrader 5 terminal.
        """

        if self.connected:
            return True

        self._require_mt5()

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

        if (
            self.connected
            and mt5 is not None
        ):
            mt5.shutdown()

        self.connected = False

    # ======================================================
    # SYMBOL RESOLUTION
    # ======================================================

    def resolve_symbol(
        self,
        symbol: str,
    ) -> str:
        """
        Resolve an Aladdin logical symbol to the
        actual symbol available in MetaTrader 5.

        Examples:

            EUR/USD -> EURUSD
            GBP/USD -> GBPUSD
            XAU/USD -> XAUUSD or GOLD
        """

        self.connect()

        return MT5SymbolResolver.resolve(
            symbol=symbol,
            mt5_module=mt5,
        )

    # ======================================================
    # MARKET DATA
    # ======================================================

    def get_candles(
        self,
        symbol,
        timeframe,
        count=100,
    ):
        """
        Get recent candles from MetaTrader 5.

        The supplied symbol can be either:

            EUR/USD
            EURUSD
            GBP/USD
            XAU/USD

        The symbol is resolved automatically to the
        broker's available MT5 symbol.
        """

        self.connect()

        # ==============================================
        # Resolve logical symbol to broker symbol
        # ==============================================

        resolved_symbol = self.resolve_symbol(
            symbol
        )

        # ==============================================
        # Make sure the symbol is available
        # ==============================================

        if not mt5.symbol_select(
            resolved_symbol,
            True,
        ):
            error = mt5.last_error()

            raise RuntimeError(
                f"Unable to select MT5 symbol "
                f"{resolved_symbol}: {error}"
            )

        # ==============================================
        # Get candle data
        # ==============================================

        rates = mt5.copy_rates_from_pos(
            resolved_symbol,
            timeframe,
            0,
            count,
        )

        if rates is None:
            error = mt5.last_error()

            raise RuntimeError(
                f"Unable to retrieve market data "
                f"for {resolved_symbol}: {error}"
            )

        if len(rates) == 0:
            raise RuntimeError(
                f"No market candles available "
                f"for {resolved_symbol}."
            )

        # ==============================================
        # Convert MT5 rates into Candle objects
        # ==============================================

        candles = []

        for rate in rates:

            timestamp = datetime.fromtimestamp(
                int(rate["time"]),
                tz=timezone.utc,
            )

            candle = Candle(
                symbol=resolved_symbol,
                timeframe=str(timeframe),
                open_price=float(
                    rate["open"]
                ),
                high_price=float(
                    rate["high"]
                ),
                low_price=float(
                    rate["low"]
                ),
                close_price=float(
                    rate["close"]
                ),
                volume=float(
                    rate["tick_volume"]
                ),
                timestamp=timestamp,
            )

            candles.append(candle)

        return candles