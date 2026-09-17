"""
mt5_provider.py

Provides real Forex market data from MetaTrader 5
for the Aladdin Forex Trading Assistant.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from datetime import datetime, timezone

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

from app.config.instrument_config import (
    normalize_symbol,
)
from app.market.candle import Candle
from app.market.mt5_symbol_resolver import (
    MT5SymbolResolver,
)
from app.mt5.mt5_session import MT5_SESSION_LOCK


class MT5DataProvider:
    """
    Get read-only Forex market data from MetaTrader 5.

    MetaTrader5 is an optional dependency so that
    Aladdin can still be imported and tested on
    non-Windows environments such as GitHub Actions.

    Real MT5 market data requires Windows with the
    MetaTrader5 Python package installed.

    Real MT5 access is protected by the shared
    process-level MT5 session lock so concurrent
    FastAPI requests cannot shut down the MT5 Python
    session while another request is using it.
    """

    def __init__(self):
        """
        Create the MT5 data provider.
        """

        self.connected = False
        self._session_lock_acquired = False

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

        A shared process-level lock is held for the
        lifetime of this provider session. This prevents
        another request from calling mt5.shutdown() while
        this provider is reading quotes or candles.
        """

        if self.connected:
            return True

        self._require_mt5()

        MT5_SESSION_LOCK.acquire()
        self._session_lock_acquired = True

        try:
            if not mt5.initialize():
                error = mt5.last_error()

                raise RuntimeError(
                    f"Unable to connect to MetaTrader 5: {error}"
                )

            self.connected = True

            return True

        except Exception:
            try:
                mt5.shutdown()
            finally:
                self.connected = False

                if self._session_lock_acquired:
                    self._session_lock_acquired = False
                    MT5_SESSION_LOCK.release()

            raise

    def disconnect(self):
        """
        Disconnect from MetaTrader 5 and release the
        shared process-level MT5 session lock.
        """

        try:
            if (
                self.connected
                and mt5 is not None
                and self._session_lock_acquired
            ):
                mt5.shutdown()

        finally:
            self.connected = False

            if self._session_lock_acquired:
                self._session_lock_acquired = False
                MT5_SESSION_LOCK.release()

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
    # SYMBOL SELECTION
    # ======================================================

    def _select_symbol(
        self,
        symbol: str,
    ) -> str:
        """
        Resolve and select an MT5 broker symbol.

        This is a read-only market-data helper.
        It does not create, modify, or close trades.
        """

        self.connect()

        resolved_symbol = self.resolve_symbol(
            symbol
        )

        if not mt5.symbol_select(
            resolved_symbol,
            True,
        ):
            error = mt5.last_error()

            raise RuntimeError(
                f"Unable to select MT5 symbol "
                f"{resolved_symbol}: {error}"
            )

        return resolved_symbol

    # ======================================================
    # LIVE MARKET QUOTE
    # ======================================================

    def get_quote(
        self,
        symbol: str,
    ) -> dict:
        """
        Return the latest read-only MT5 quote.

        The supplied symbol may be an Aladdin display
        symbol, logical symbol, or supported MT5 alias.

        Examples:

            EUR/USD
            EURUSD
            USDJPY
            XAU/USD
            GOLD

        Returned data includes:

            symbol
            broker_symbol
            bid
            ask
            spread
            spread_points
            digits
            point
            time

        No trade execution is performed.
        """

        logical_symbol = normalize_symbol(
            symbol
        )

        resolved_symbol = self._select_symbol(
            logical_symbol
        )

        symbol_info = mt5.symbol_info(
            resolved_symbol
        )

        if symbol_info is None:
            raise RuntimeError(
                f"Unable to retrieve MT5 symbol "
                f"information for {resolved_symbol}."
            )

        tick = mt5.symbol_info_tick(
            resolved_symbol
        )

        if tick is None:
            error = mt5.last_error()

            raise RuntimeError(
                f"No MT5 market tick is available "
                f"for {resolved_symbol}: {error}"
            )

        bid = float(
            tick.bid
        )

        ask = float(
            tick.ask
        )

        if bid <= 0 or ask <= 0:
            raise RuntimeError(
                f"Invalid MT5 bid/ask prices "
                f"for {resolved_symbol}."
            )

        if ask < bid:
            raise RuntimeError(
                f"Invalid MT5 quote spread "
                f"for {resolved_symbol}."
            )

        point = float(
            symbol_info.point
        )

        if point <= 0:
            raise RuntimeError(
                f"Invalid MT5 point size "
                f"for {resolved_symbol}."
            )

        digits = int(
            symbol_info.digits
        )

        spread = (
            ask - bid
        )

        spread_points = (
            spread / point
        )

        tick_time = int(
            getattr(
                tick,
                "time",
                0,
            )
            or 0
        )

        return {
            "symbol": logical_symbol,
            "broker_symbol": resolved_symbol,
            "bid": round(
                bid,
                digits,
            ),
            "ask": round(
                ask,
                digits,
            ),
            "spread": round(
                spread,
                digits,
            ),
            "spread_points": round(
                spread_points,
                2,
            ),
            "digits": digits,
            "point": point,
            "time": tick_time,
        }

    # ======================================================
    # ACCOUNT RISK INFORMATION
    # ======================================================

    def get_account_risk_info(
        self,
    ) -> dict:
        """
        Return the read-only MT5 account information required
        by the deterministic pre-trade RiskService.

        This method does not calculate risk, determine trade
        direction, size positions, or execute trades.
        """

        self.connect()

        account_info = mt5.account_info()

        if account_info is None:
            error = mt5.last_error()

            raise RuntimeError(
                "Unable to retrieve MT5 account "
                f"information: {error}"
            )

        equity = float(
            account_info.equity
        )

        balance = float(
            account_info.balance
        )

        margin = float(
            account_info.margin
        )

        margin_free = float(
            account_info.margin_free
        )

        if equity <= 0:
            raise RuntimeError(
                "Invalid MT5 account equity."
            )

        return {
            "equity": equity,
            "balance": balance,
            "margin": margin,
            "margin_free": margin_free,
        }

    # ======================================================
    # SYMBOL RISK INFORMATION
    # ======================================================

    def get_symbol_risk_info(
        self,
        symbol: str,
    ) -> dict:
        """
        Return broker symbol specifications required by
        the deterministic pre-trade RiskService.

        Values come directly from MT5 symbol_info().

        This method performs no position sizing and no
        trade execution.
        """

        logical_symbol = normalize_symbol(
            symbol
        )

        resolved_symbol = self._select_symbol(
            logical_symbol
        )

        symbol_info = mt5.symbol_info(
            resolved_symbol
        )

        if symbol_info is None:
            error = mt5.last_error()

            raise RuntimeError(
                "Unable to retrieve MT5 symbol "
                f"information for {resolved_symbol}: "
                f"{error}"
            )

        trade_tick_size = float(
            symbol_info.trade_tick_size
        )

        trade_tick_value = float(
            symbol_info.trade_tick_value
        )

        volume_min = float(
            symbol_info.volume_min
        )

        volume_max = float(
            symbol_info.volume_max
        )

        volume_step = float(
            symbol_info.volume_step
        )

        if trade_tick_size <= 0:
            raise RuntimeError(
                "Invalid MT5 trade tick size for "
                f"{resolved_symbol}."
            )

        if trade_tick_value <= 0:
            raise RuntimeError(
                "Invalid MT5 trade tick value for "
                f"{resolved_symbol}."
            )

        if volume_min <= 0:
            raise RuntimeError(
                "Invalid MT5 minimum volume for "
                f"{resolved_symbol}."
            )

        if volume_max <= 0:
            raise RuntimeError(
                "Invalid MT5 maximum volume for "
                f"{resolved_symbol}."
            )

        if volume_step <= 0:
            raise RuntimeError(
                "Invalid MT5 volume step for "
                f"{resolved_symbol}."
            )

        if volume_min > volume_max:
            raise RuntimeError(
                "Invalid MT5 volume range for "
                f"{resolved_symbol}."
            )

        return {
            "symbol": logical_symbol,
            "broker_symbol": resolved_symbol,
            "trade_tick_size": trade_tick_size,
            "trade_tick_value": trade_tick_value,
            "volume_min": volume_min,
            "volume_max": volume_max,
            "volume_step": volume_step,
        }

    # ======================================================
    # MARKET CANDLES
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
