"""
mt5_connector.py

Handles MetaTrader 5 connection,
order preparation, validation,
and DEMO execution safety.

Author: Tharindu Kothalawala
Project: Aladdin
"""

import os
from dataclasses import dataclass

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

from app.mt5.mt5_session import MT5_SESSION_LOCK


@dataclass
class MT5OrderRequest:
    """
    Represents a prepared MT5 order request.
    """

    symbol: str
    order_type: str
    volume: float
    status: str

    mt5_symbol: str | None = None

    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None

    # Local execution database ID.
    #
    # When available, this value is written
    # into the MT5 order comment so a broker
    # order can be correlated with its local
    # PENDING audit record.
    execution_id: int | None = None


@dataclass
class MT5ExecutionResult:
    """
    Represents the result of an MT5 execution.
    """

    success: bool
    message: str
    order_id: str | None = None


class MT5Connector:
    """
    Handles MetaTrader 5 communication.

    Supported modes:

    MOCK
        Used for automated tests and
        normal development.

    DEMO
        Connects only to an MT5 demo account.

    LIVE accounts are intentionally blocked.

    DEMO order sending also requires:

    ALADDIN_ENABLE_DEMO_EXECUTION=true

    This provides a second safety switch so
    connecting to MT5 does not automatically
    allow order submission.
    """

    def __init__(
        self,
        mode: str | None = None,
    ):
        configured_mode = (
            mode
            or os.getenv(
                "ALADDIN_MT5_MODE",
                "MOCK",
            )
        )

        self.mode = configured_mode.upper()

        if self.mode not in {
            "MOCK",
            "DEMO",
        }:
            raise ValueError(
                "ALADDIN_MT5_MODE must be "
                "MOCK or DEMO."
            )

        self.connected = False
        self.account_info = None
        self._session_lock_acquired = False

    # ======================================================
    # MT5 AVAILABILITY
    # ======================================================

    @staticmethod
    def _require_mt5():
        """
        Ensure the MetaTrader5 Python package is available.

        MOCK mode does not require MetaTrader5. This allows
        Linux CI environments to import and test Aladdin while
        real/demo MT5 functionality remains available on Windows.
        """

        if mt5 is None:
            raise RuntimeError(
                "MetaTrader5 is not installed on this platform. "
                "MT5 DEMO mode requires Windows with the "
                "MetaTrader5 Python package installed."
            )

        return mt5

    # ======================================================
    # CONNECTION
    # ======================================================

    def connect(self):
        """
        Connect to MetaTrader 5.

        MOCK mode:
            Simulates the connection.

        DEMO mode:
            Acquires the shared process-level MT5 session
            lock, connects to the installed MT5 terminal,
            and verifies that the active account is DEMO.

        The lock remains held for the lifetime of this
        connector session and is released by disconnect().
        This prevents another FastAPI request from calling
        mt5.shutdown() while this request is using MT5.
        """

        if self.connected:
            return True

        if self.mode == "MOCK":
            self.connected = True
            return True

        self._require_mt5()

        MT5_SESSION_LOCK.acquire()
        self._session_lock_acquired = True

        try:
            initialized = mt5.initialize()

            if not initialized:
                error = mt5.last_error()
                raise ConnectionError(
                    f"MT5 initialization failed: {error}"
                )

            account = mt5.account_info()

            if account is None:
                raise ConnectionError(
                    "MT5 account information is unavailable."
                )

            if (
                account.trade_mode
                != mt5.ACCOUNT_TRADE_MODE_DEMO
            ):
                raise PermissionError(
                    "Aladdin DEMO execution requires "
                    "an MT5 demo account. "
                    "Live accounts are blocked."
                )

            if not account.trade_allowed:
                raise PermissionError(
                    "Trading is not allowed "
                    "on the connected MT5 account."
                )

            if not account.trade_expert:
                raise PermissionError(
                    "Expert/API trading is not "
                    "allowed on the connected "
                    "MT5 account."
                )

            terminal = mt5.terminal_info()

            if terminal is None:
                raise ConnectionError(
                    "MT5 terminal information is unavailable."
                )

            if not terminal.connected:
                raise ConnectionError(
                    "MT5 terminal is not connected "
                    "to the broker server."
                )

            self.account_info = account
            self.connected = True
            return True

        except Exception:
            try:
                mt5.shutdown()
            finally:
                self.connected = False
                self.account_info = None

                if self._session_lock_acquired:
                    self._session_lock_acquired = False
                    MT5_SESSION_LOCK.release()

            raise

    # ======================================================
    # DISCONNECT
    # ======================================================

    def disconnect(self):
        """
        Disconnect from MT5 and release the shared session lock.

        Only a connector instance that acquired the shared
        MT5 session lock may shut down the real MT5 Python
        connection.
        """

        try:
            if (
                self.mode == "DEMO"
                and mt5 is not None
                and self._session_lock_acquired
            ):
                mt5.shutdown()

        finally:
            self.connected = False
            self.account_info = None

            if self._session_lock_acquired:
                self._session_lock_acquired = False
                MT5_SESSION_LOCK.release()

    # ======================================================
    # SYMBOL NORMALIZATION
    # ======================================================

    @staticmethod
    def normalize_symbol(
        symbol: str,
    ) -> str:
        """
        Convert application symbols.

        Examples:

        EUR/USD -> EURUSD
        EUR-USD  -> EURUSD
        EUR_USD  -> EURUSD
        """

        return (
            symbol
            .strip()
            .upper()
            .replace("/", "")
            .replace("-", "")
            .replace("_", "")
        )

    # ======================================================
    # VOLUME VALIDATION
    # ======================================================

    @staticmethod
    def _volume_is_valid(
        volume: float,
        minimum: float,
        maximum: float,
        step: float,
    ) -> bool:
        """
        Validate broker lot-size rules.
        """

        if (
            volume < minimum
            or volume > maximum
        ):
            return False

        if step <= 0:
            return True

        steps = round(
            (volume - minimum)
            / step
        )

        expected_volume = (
            minimum
            + steps * step
        )

        return (
            abs(
                expected_volume
                - volume
            )
            < 1e-9
        )

    # ======================================================
    # PRICE VALIDATION
    # ======================================================

    @staticmethod
    def _validate_price_structure(
        order_type,
        reference_price,
        stop_loss,
        take_profit,
    ):
        """
        Validate SL and TP placement.

        BUY:
            SL < PRICE < TP

        SELL:
            TP < PRICE < SL
        """

        if (
            reference_price <= 0
            or stop_loss <= 0
            or take_profit <= 0
        ):
            raise ValueError(
                "Entry price, stop loss and "
                "take profit must be greater "
                "than zero."
            )

        if order_type == "BUY":

            if not (
                stop_loss
                < reference_price
                < take_profit
            ):
                raise ValueError(
                    "Invalid BUY price structure. "
                    "Required: "
                    "stop_loss < price < take_profit."
                )

        elif order_type == "SELL":

            if not (
                take_profit
                < reference_price
                < stop_loss
            ):
                raise ValueError(
                    "Invalid SELL price structure. "
                    "Required: "
                    "take_profit < price < stop_loss."
                )

    # ======================================================
    # FILLING MODE
    # ======================================================

    @staticmethod
    def _get_filling_mode(
        symbol_info,
    ):
        """
        Convert the broker symbol filling flags
        into an MT5 order filling mode.

        Symbol filling flags:

        1 -> FOK
        2 -> IOC

        RETURN is used as fallback.
        """

        MT5Connector._require_mt5()

        filling_flags = int(
            symbol_info.filling_mode
        )

        if filling_flags & 1:
            return mt5.ORDER_FILLING_FOK

        if filling_flags & 2:
            return mt5.ORDER_FILLING_IOC

        return mt5.ORDER_FILLING_RETURN

    # ======================================================
    # EXECUTION CORRELATION
    # ======================================================

    @staticmethod
    def _validate_execution_id(
        execution_id,
    ):
        """
        Validate the optional local execution ID.

        The execution ID comes from the committed
        PENDING execution database row.

        Direct MT5 connector usage may omit it,
        but when supplied it must be a positive
        integer.
        """

        if execution_id is None:
            return

        if (
            isinstance(execution_id, bool)
            or not isinstance(
                execution_id,
                int,
            )
            or execution_id <= 0
        ):
            raise ValueError(
                "Execution ID must be a "
                "positive integer."
            )

    @staticmethod
    def _build_execution_comment(
        execution_id,
    ) -> str:
        """
        Build the MT5 broker comment.

        Correlated execution example:

            ALADDIN E123

        When there is no execution ID, preserve
        the legacy development comment.
        """

        if execution_id is None:
            return "ALADDIN DEMO"

        return (
            f"ALADDIN E{execution_id}"
        )

    # ======================================================
    # PREPARE ORDER
    # ======================================================

    def prepare_order(
        self,
        symbol,
        order_type,
        volume,
        entry_price=None,
        stop_loss=None,
        take_profit=None,
        execution_id=None,
    ):
        """
        Prepare an order request.

        MOCK:
            Keeps automated tests working.

        DEMO:
            Validates the real broker symbol,
            lot size, market price, SL and TP.

        execution_id:
            Optional local execution database ID
            used for broker correlation.
        """

        if not self.connected:
            raise ConnectionError(
                "MT5 is not connected."
            )

        # ==========================================
        # Basic Validation
        # ==========================================

        if (
            not symbol
            or not symbol.strip()
        ):
            raise ValueError(
                "Order symbol cannot be empty."
            )

        order_type = (
            order_type
            .strip()
            .upper()
        )

        if order_type not in {
            "BUY",
            "SELL",
        }:
            raise ValueError(
                "Order type must be "
                "BUY or SELL."
            )

        if volume <= 0:
            raise ValueError(
                "Order volume must be "
                "greater than zero."
            )

        self._validate_execution_id(
            execution_id
        )

        original_symbol = (
            symbol.strip().upper()
        )

        # ==========================================
        # Price Parameters
        # ==========================================

        supplied_prices = [
            entry_price is not None,
            stop_loss is not None,
            take_profit is not None,
        ]

        if (
            any(supplied_prices)
            and not all(supplied_prices)
        ):
            raise ValueError(
                "Entry price, stop loss and "
                "take profit must be supplied "
                "together."
            )

        # ==========================================
        # MOCK MODE
        # ==========================================

        if self.mode == "MOCK":

            if all(supplied_prices):
                self._validate_price_structure(
                    order_type=order_type,
                    reference_price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                )

            return MT5OrderRequest(
                symbol=original_symbol,
                order_type=order_type,
                volume=volume,
                status="READY",
                mt5_symbol=None,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                execution_id=execution_id,
            )

        # ==========================================
        # DEMO Requires MT5
        # ==========================================

        self._require_mt5()

        # ==========================================
        # DEMO Requires SL / TP
        # ==========================================

        if not all(supplied_prices):
            raise ValueError(
                "DEMO execution requires "
                "entry price, stop loss and "
                "take profit."
            )

        # ==========================================
        # MT5 Symbol
        # ==========================================

        mt5_symbol = (
            self.normalize_symbol(
                symbol
            )
        )

        symbol_info = (
            mt5.symbol_info(
                mt5_symbol
            )
        )

        if symbol_info is None:
            raise ValueError(
                f"MT5 symbol not found: "
                f"{mt5_symbol}"
            )

        # ==========================================
        # Enable Symbol
        # ==========================================

        if not symbol_info.visible:

            selected = (
                mt5.symbol_select(
                    mt5_symbol,
                    True,
                )
            )

            if not selected:
                raise ValueError(
                    "Unable to enable symbol: "
                    f"{mt5_symbol}"
                )

            symbol_info = (
                mt5.symbol_info(
                    mt5_symbol
                )
            )

            if symbol_info is None:
                raise ValueError(
                    "Unable to reload symbol "
                    f"information for {mt5_symbol}."
                )

        # ==========================================
        # Trading Enabled
        # ==========================================

        if (
            symbol_info.trade_mode
            == mt5.SYMBOL_TRADE_MODE_DISABLED
        ):
            raise ValueError(
                f"Trading is disabled "
                f"for {mt5_symbol}."
            )

        # ==========================================
        # Broker Volume Validation
        # ==========================================

        if not self._volume_is_valid(
            volume=volume,
            minimum=(
                symbol_info.volume_min
            ),
            maximum=(
                symbol_info.volume_max
            ),
            step=(
                symbol_info.volume_step
            ),
        ):
            raise ValueError(
                "Invalid volume for "
                f"{mt5_symbol}. "
                f"Minimum="
                f"{symbol_info.volume_min}, "
                f"Maximum="
                f"{symbol_info.volume_max}, "
                f"Step="
                f"{symbol_info.volume_step}"
            )

        # ==========================================
        # Current Market Tick
        # ==========================================

        tick = (
            mt5.symbol_info_tick(
                mt5_symbol
            )
        )

        if tick is None:
            raise ValueError(
                "No market tick available "
                f"for {mt5_symbol}."
            )

        if (
            tick.bid <= 0
            or tick.ask <= 0
        ):
            raise ValueError(
                "Invalid market price "
                f"for {mt5_symbol}."
            )

        # ==========================================
        # Validate Planned Price Structure
        # ==========================================

        self._validate_price_structure(
            order_type=order_type,
            reference_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

        # ==========================================
        # Validate Against Current Price
        # ==========================================
        #
        # Market orders execute at:
        #
        # BUY  -> Ask
        # SELL -> Bid
        #
        # The planned entry price is therefore
        # reference information only.
        # ==========================================

        if order_type == "BUY":
            current_price = tick.ask
        else:
            current_price = tick.bid

        self._validate_price_structure(
            order_type=order_type,
            reference_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

        # ==========================================
        # Spread Safety
        # ==========================================

        point = symbol_info.point

        if point <= 0:
            raise ValueError(
                f"Invalid broker point size "
                f"for {mt5_symbol}."
            )

        spread_points = (
            tick.ask - tick.bid
        ) / point

        max_spread_points = float(
            os.getenv(
                "ALADDIN_MAX_SPREAD_POINTS",
                "100",
            )
        )

        if spread_points < 0:
            raise ValueError(
                f"Invalid negative spread "
                f"for {mt5_symbol}."
            )

        if (
            spread_points
            > max_spread_points
        ):
            raise ValueError(
                f"Spread too high for "
                f"{mt5_symbol}. "
                f"Current="
                f"{spread_points:.1f} points, "
                f"Maximum="
                f"{max_spread_points:.1f} points."
            )

        # ==========================================
        # Prepared Request
        # ==========================================

        return MT5OrderRequest(
            symbol=original_symbol,
            order_type=order_type,
            volume=volume,
            status="READY",
            mt5_symbol=mt5_symbol,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            execution_id=execution_id,
        )

    # ======================================================
    # REVALIDATE DEMO ACCOUNT
    # ======================================================

    @staticmethod
    def _validate_demo_account():
        """
        Re-check the account immediately before
        sending an order.

        This prevents execution if the user
        switched from a demo account to another
        account after connecting.
        """

        MT5Connector._require_mt5()

        account = mt5.account_info()

        if account is None:
            raise ConnectionError(
                "MT5 account information "
                "is unavailable."
            )

        if (
            account.trade_mode
            != mt5.ACCOUNT_TRADE_MODE_DEMO
        ):
            raise PermissionError(
                "Order blocked because the "
                "connected account is not DEMO."
            )

        if not account.trade_allowed:
            raise PermissionError(
                "Trading is not allowed "
                "on the connected account."
            )

        if not account.trade_expert:
            raise PermissionError(
                "Expert/API trading is not "
                "allowed on the connected account."
            )

        return account

    # ======================================================
    # BUILD REAL MT5 REQUEST
    # ======================================================

    def _build_mt5_request(
        self,
        order_request,
    ):
        """
        Convert the Aladdin order into an
        MT5 market-order request.

        When an execution ID exists, the
        broker comment contains the same
        local audit identifier.

        Example:

            ALADDIN E123
        """

        self._require_mt5()

        mt5_symbol = (
            order_request.mt5_symbol
        )

        if not mt5_symbol:
            raise ValueError(
                "Prepared MT5 symbol is missing."
            )

        symbol_info = (
            mt5.symbol_info(
                mt5_symbol
            )
        )

        if symbol_info is None:
            raise ValueError(
                f"MT5 symbol not found: "
                f"{mt5_symbol}"
            )

        tick = (
            mt5.symbol_info_tick(
                mt5_symbol
            )
        )

        if tick is None:
            raise ValueError(
                "No market tick available "
                f"for {mt5_symbol}."
            )

        # ==========================================
        # Market Price
        # ==========================================

        if order_request.order_type == "BUY":

            market_price = tick.ask

            mt5_order_type = (
                mt5.ORDER_TYPE_BUY
            )

        else:

            market_price = tick.bid

            mt5_order_type = (
                mt5.ORDER_TYPE_SELL
            )

        if market_price <= 0:
            raise ValueError(
                f"Invalid execution price "
                f"for {mt5_symbol}."
            )

        # ==========================================
        # Revalidate SL / TP at Execution Time
        # ==========================================

        self._validate_price_structure(
            order_type=(
                order_request.order_type
            ),
            reference_price=market_price,
            stop_loss=(
                order_request.stop_loss
            ),
            take_profit=(
                order_request.take_profit
            ),
        )

        # ==========================================
        # Broker Digits
        # ==========================================

        digits = int(
            symbol_info.digits
        )

        market_price = round(
            market_price,
            digits,
        )

        stop_loss = round(
            order_request.stop_loss,
            digits,
        )

        take_profit = round(
            order_request.take_profit,
            digits,
        )

        # ==========================================
        # Deviation
        # ==========================================

        deviation = int(
            os.getenv(
                "ALADDIN_MT5_DEVIATION",
                "20",
            )
        )

        # ==========================================
        # Filling Mode
        # ==========================================

        filling_mode = (
            self._get_filling_mode(
                symbol_info
            )
        )

        # ==========================================
        # Correlation Comment
        # ==========================================

        execution_comment = (
            self._build_execution_comment(
                order_request.execution_id
            )
        )

        # ==========================================
        # Real MT5 Request
        # ==========================================

        return {
            "action": (
                mt5.TRADE_ACTION_DEAL
            ),
            "symbol": mt5_symbol,
            "volume": float(
                order_request.volume
            ),
            "type": mt5_order_type,
            "price": market_price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": deviation,
            "magic": 20260911,
            "comment": execution_comment,
            "type_time": (
                mt5.ORDER_TIME_GTC
            ),
            "type_filling": (
                filling_mode
            ),
        }

    # ======================================================
    # SEND ORDER
    # ======================================================

    def send_order(
        self,
        order_request,
    ):
        """
        Send a prepared order.

        MOCK:
            Returns the existing fake order result.

        DEMO:
            1. Revalidates demo account.
            2. Builds real MT5 request.
            3. Runs mt5.order_check().
            4. Requires second execution switch.
            5. Sends order using mt5.order_send().
        """

        if not self.connected:
            raise ConnectionError(
                "MT5 is not connected."
            )

        if (
            order_request.status
            != "READY"
        ):
            raise ValueError(
                "MT5 order is not ready "
                "for execution."
            )

        # ==========================================
        # MOCK MODE
        # ==========================================

        if self.mode == "MOCK":

            return MT5ExecutionResult(
                success=True,
                message=(
                    "Mock order executed "
                    "successfully."
                ),
                order_id=(
                    "MOCK_ORDER_001"
                ),
            )

        # ==========================================
        # DEMO ACCOUNT SAFETY
        # ==========================================

        self._validate_demo_account()

        # ==========================================
        # Build Broker Request
        # ==========================================

        request = (
            self._build_mt5_request(
                order_request
            )
        )

        # ==========================================
        # MT5 Pre-Trade Check
        # ==========================================

        check_result = (
            mt5.order_check(
                request
            )
        )

        if check_result is None:

            error = mt5.last_error()

            return MT5ExecutionResult(
                success=False,
                message=(
                    "MT5 order_check failed. "
                    f"Error: {error}"
                ),
                order_id=None,
            )

        # order_check retcode 0 means
        # the request passed broker checks.

        if check_result.retcode != 0:

            return MT5ExecutionResult(
                success=False,
                message=(
                    "MT5 order check rejected "
                    "the trade. "
                    f"Retcode="
                    f"{check_result.retcode}, "
                    f"Comment="
                    f"{check_result.comment}"
                ),
                order_id=None,
            )

        # ==========================================
        # SECOND SAFETY SWITCH
        # ==========================================

        demo_execution_enabled = (
            os.getenv(
                "ALADDIN_ENABLE_DEMO_EXECUTION",
                "false",
            )
            .strip()
            .lower()
            == "true"
        )

        if not demo_execution_enabled:

            return MT5ExecutionResult(
                success=False,
                message=(
                    "MT5 DEMO order passed "
                    "order_check but execution "
                    "is safety-locked. "
                    "Set "
                    "ALADDIN_ENABLE_DEMO_EXECUTION"
                    "=true to allow DEMO orders."
                ),
                order_id=None,
            )

        # ==========================================
        # Send DEMO Order
        # ==========================================

        result = (
            mt5.order_send(
                request
            )
        )

        if result is None:

            error = mt5.last_error()

            return MT5ExecutionResult(
                success=False,
                message=(
                    "MT5 order_send failed. "
                    f"Error: {error}"
                ),
                order_id=None,
            )

        # ==========================================
        # Successful MT5 Retcodes
        # ==========================================

        successful_retcodes = {
            mt5.TRADE_RETCODE_DONE,
            mt5.TRADE_RETCODE_PLACED,
            mt5.TRADE_RETCODE_DONE_PARTIAL,
        }

        if (
            result.retcode
            not in successful_retcodes
        ):

            return MT5ExecutionResult(
                success=False,
                message=(
                    "MT5 rejected the order. "
                    f"Retcode="
                    f"{result.retcode}, "
                    f"Comment="
                    f"{result.comment}"
                ),
                order_id=None,
            )

        # ==========================================
        # Broker Order ID
        # ==========================================

        broker_id = None

        if getattr(
            result,
            "order",
            0,
        ):

            broker_id = str(
                result.order
            )

        elif getattr(
            result,
            "deal",
            0,
        ):

            broker_id = str(
                result.deal
            )

        return MT5ExecutionResult(
            success=True,
            message=(
                "MT5 DEMO order executed "
                "successfully."
            ),
            order_id=broker_id,
        )