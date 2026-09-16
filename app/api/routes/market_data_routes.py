"""
market_data_routes.py

Authenticated read-only MT5 market-data endpoints
for the Aladdin V2 Trading Terminal.

Provides real OHLC candle data and live bid/ask
quotes from the connected MetaTrader 5 terminal.

These endpoints do not create, modify,
or close broker trades.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from app.auth.dependencies import (
    get_current_user,
)

from app.auth.models import UserModel

from app.config.instrument_config import (
    INSTRUMENTS,
    get_display_symbol,
)

from app.market.indicators import (
    TechnicalIndicators,
)

from app.market.mt5_provider import (
    MT5DataProvider,
)

from app.services.chart_indicator_service import (
    ChartIndicatorService,
)

from app.services.market_structure_service import (
    MarketStructureService,
)


router = APIRouter(
    prefix="/market-data",
    tags=["Market Data"],
)


# ==========================================================
# SUPPORTED SYMBOLS
# ==========================================================

MARKET_WATCH_SYMBOLS = tuple(
    INSTRUMENTS.keys()
)

SUPPORTED_SYMBOLS = set(
    MARKET_WATCH_SYMBOLS
)


# ==========================================================
# MARKET STRUCTURE CONFIGURATION
# ==========================================================

SUPPORT_RESISTANCE_ATR_PERIOD = 14

SUPPORT_RESISTANCE_TOLERANCE_MULTIPLIER = 0.25

SUPPORT_RESISTANCE_MIN_TOUCHES = 2

DISPLACEMENT_BODY_ATR_MULTIPLIER = 1.5


# Equal High / Equal Low detection uses ATR-normalized
# tolerance independently from support/resistance.
EQUAL_HIGH_LOW_TOLERANCE_MULTIPLIER = 0.15

EQUAL_HIGH_LOW_MIN_TOUCHES = 2


# ==========================================================
# SYMBOL NORMALIZATION
# ==========================================================

def _normalize_symbol(
    symbol: str,
) -> str:
    """
    Normalize a frontend symbol into the logical
    Aladdin symbol format.

    Examples:

        EUR/USD -> EURUSD
        EURUSD  -> EURUSD
        eur/usd -> EURUSD
    """

    normalized = (
        symbol
        .strip()
        .upper()
        .replace("/", "")
        .replace(" ", "")
    )

    if normalized not in SUPPORTED_SYMBOLS:
        raise ValueError(
            f"Unsupported Aladdin trading symbol: {symbol}."
        )

    return normalized


# ==========================================================
# TIMEFRAME RESOLUTION
# ==========================================================

def _resolve_timeframe(
    provider: MT5DataProvider,
    timeframe: str,
):
    """
    Convert a frontend chart timeframe name into
    the corresponding MetaTrader 5 constant.

    ALADDIN V2 chart timeframes:

        M1  - 1 minute
        M5  - 5 minutes
        M15 - 15 minutes
        M30 - 30 minutes
        H1  - 1 hour
        H4  - 4 hours
        D1  - 1 day
        W1  - 1 week

    The current ALADDIN multi-timeframe AI model
    still uses:

        M15 - Entry timeframe
        H1  - Primary timeframe
        H4  - Higher timeframe

    Extra chart timeframes are for market inspection
    only and do not change AI decision authority.
    """

    mt5_module = provider._require_mt5()

    normalized = (
        timeframe
        .strip()
        .upper()
    )

    timeframe_map = {
        "M1": mt5_module.TIMEFRAME_M1,
        "M5": mt5_module.TIMEFRAME_M5,
        "M15": mt5_module.TIMEFRAME_M15,
        "M30": mt5_module.TIMEFRAME_M30,
        "H1": mt5_module.TIMEFRAME_H1,
        "H4": mt5_module.TIMEFRAME_H4,
        "D1": mt5_module.TIMEFRAME_D1,
        "W1": mt5_module.TIMEFRAME_W1,
    }

    if normalized not in timeframe_map:
        raise ValueError(
            "Unsupported timeframe. "
            "Supported timeframes are "
            "M1, M5, M15, M30, H1, H4, D1, and W1."
        )

    return (
        normalized,
        timeframe_map[normalized],
    )


# ==========================================================
# MARKET STRUCTURE SERIALIZATION
# ==========================================================

def _serialize_swing_point(
    point: dict,
) -> dict:
    """
    Convert an internal market-structure swing point
    into the frontend chart contract.
    """

    return {
        "index": point["index"],
        "price": point["price"],
        "time": int(
            point["timestamp"].timestamp()
        ),
    }


def _serialize_structure_event(
    event: dict | None,
) -> dict | None:
    """
    Convert an internal BOS or CHoCH event into
    the frontend chart contract.
    """

    if event is None:
        return None

    return {
        "type": event["type"],
        "broken_price": event["broken_price"],
        "swing_index": event["swing_index"],
        "break_index": event["break_index"],
        "time": int(
            event["timestamp"].timestamp()
        ),
    }


def _serialize_order_block(
    event: dict | None,
) -> dict | None:
    """
    Convert an internal Order Block event into
    the frontend chart contract.
    """

    if event is None:
        return None

    return {
        "type": event["type"],
        "candle_index": event["candle_index"],
        "high_price": event["high_price"],
        "low_price": event["low_price"],
        "open_price": event["open_price"],
        "close_price": event["close_price"],
        "time": int(
            event["timestamp"].timestamp()
        ),
    }


def _serialize_fvg(
    event: dict | None,
) -> dict | None:
    """
    Convert an internal Fair Value Gap event into
    the frontend chart contract.
    """

    if event is None:
        return None

    return {
        "type": event["type"],
        "start_index": event["start_index"],
        "middle_index": event["middle_index"],
        "end_index": event["end_index"],
        "lower_price": event["lower_price"],
        "upper_price": event["upper_price"],
        "time": int(
            event["timestamp"].timestamp()
        ),
    }


def _serialize_liquidity_sweep(
    event: dict | None,
) -> dict | None:
    """
    Convert an internal liquidity-sweep event into
    the frontend chart contract.
    """

    if event is None:
        return None

    return {
        "type": event["type"],
        "level_price": event["level_price"],
        "swing_index": event["swing_index"],
        "sweep_index": event["sweep_index"],
        "time": int(
            event["timestamp"].timestamp()
        ),
    }


def _serialize_engulfing(
    event: dict | None,
) -> dict | None:
    """
    Convert an internal engulfing-pattern event
    into the frontend chart contract.
    """

    if event is None:
        return None

    return {
        "type": event["type"],
        "previous_index": event["previous_index"],
        "engulfing_index": event["engulfing_index"],
        "open_price": event["open_price"],
        "close_price": event["close_price"],
        "high_price": event["high_price"],
        "low_price": event["low_price"],
        "time": int(
            event["timestamp"].timestamp()
        ),
    }


def _serialize_displacement(
    event: dict | None,
) -> dict | None:
    """
    Convert an internal displacement event
    into the frontend chart contract.
    """

    if event is None:
        return None

    return {
        "type": event["type"],
        "candle_index": event["candle_index"],
        "open_price": event["open_price"],
        "close_price": event["close_price"],
        "high_price": event["high_price"],
        "low_price": event["low_price"],
        "body_size": event["body_size"],
        "body_atr_ratio": event["body_atr_ratio"],
        "time": int(
            event["timestamp"].timestamp()
        ),
    }


def _serialize_premium_discount(
    event: dict | None,
) -> dict | None:
    """
    Convert the premium / equilibrium / discount dealing
    range into the frontend chart contract.
    """

    if event is None:
        return None

    return dict(event)


# ==========================================================
# REAL MT5 MARKET WATCH QUOTES
# ==========================================================

@router.get("/quotes")
def get_market_quotes(
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Return live read-only MT5 Market Watch data
    for all official ALADDIN trading instruments.

    Each instrument is processed independently.

    A temporary quote failure for one symbol does
    not remove valid quotes for the other symbols.

    HTTP 503 is returned only when no valid quote
    can be retrieved from MT5.

    This endpoint does not execute or modify trades.
    """

    _ = current_user

    provider = MT5DataProvider()

    quotes = []
    available_count = 0
    first_runtime_error = None

    try:

        for symbol in MARKET_WATCH_SYMBOLS:

            try:

                quote = provider.get_quote(
                    symbol
                )

                quotes.append(
                    {
                        "symbol": quote["symbol"],
                        "display_symbol": get_display_symbol(
                            quote["symbol"]
                        ),
                        "broker_symbol": quote[
                            "broker_symbol"
                        ],
                        "bid": quote["bid"],
                        "ask": quote["ask"],
                        "spread": quote["spread"],
                        "spread_points": quote[
                            "spread_points"
                        ],
                        "digits": quote["digits"],
                        "point": quote["point"],
                        "time": quote["time"],
                        "available": True,
                        "error": None,
                    }
                )

                available_count += 1

            except RuntimeError as error:

                if first_runtime_error is None:
                    first_runtime_error = str(
                        error
                    )

                quotes.append(
                    {
                        "symbol": symbol,
                        "display_symbol": get_display_symbol(
                            symbol
                        ),
                        "broker_symbol": None,
                        "bid": None,
                        "ask": None,
                        "spread": None,
                        "spread_points": None,
                        "digits": None,
                        "point": None,
                        "time": None,
                        "available": False,
                        "error": str(error),
                    }
                )

            except ValueError as error:

                quotes.append(
                    {
                        "symbol": symbol,
                        "display_symbol": get_display_symbol(
                            symbol
                        ),
                        "broker_symbol": None,
                        "bid": None,
                        "ask": None,
                        "spread": None,
                        "spread_points": None,
                        "digits": None,
                        "point": None,
                        "time": None,
                        "available": False,
                        "error": str(error),
                    }
                )

        if available_count == 0:

            raise HTTPException(
                status_code=503,
                detail=(
                    first_runtime_error
                    or "No MT5 market quotes are available."
                ),
            )

        unavailable_count = (
            len(quotes)
            - available_count
        )

        return {
            "count": len(quotes),
            "available_count": available_count,
            "unavailable_count": unavailable_count,
            "quotes": quotes,
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to retrieve MT5 "
                f"market quotes: {error}"
            ),
        )

    finally:
        provider.disconnect()


# ==========================================================
# REAL MT5 CANDLES
# ==========================================================

@router.get("/candles")
def get_market_candles(
    symbol: str = Query(
        default="EURUSD",
        description=(
            "Aladdin trading symbol, for example "
            "EURUSD, GBPUSD, USDJPY, or XAUUSD."
        ),
    ),
    timeframe: str = Query(
        default="H1",
        description=(
            "Chart timeframe. "
            "Supported values: "
            "M1, M5, M15, M30, H1, H4, D1, W1."
        ),
    ),
    count: int = Query(
        default=300,
        ge=50,
        le=5000,
        description=(
            "Number of recent MT5 candles to return."
        ),
    ),
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Return real OHLC candle data from MetaTrader 5.

    This endpoint is authenticated and read-only.

    All indicators and market-structure calculations
    reuse the same MT5 candle dataset.

    Market structure exposes:

    - swing highs
    - swing lows
    - support/resistance
    - equal highs
    - equal lows
    - BOS
    - CHoCH
    - liquidity sweep
    - Order Block
    - FVG
    - engulfing
    - displacement
    - premium/equilibrium/discount

    No trading action is performed.
    """

    _ = current_user

    provider = MT5DataProvider()

    try:

        # --------------------------------------------------
        # Normalize request
        # --------------------------------------------------

        normalized_symbol = _normalize_symbol(
            symbol
        )

        (
            normalized_timeframe,
            mt5_timeframe,
        ) = _resolve_timeframe(
            provider,
            timeframe,
        )

        # --------------------------------------------------
        # SINGLE MT5 CANDLE FETCH
        # --------------------------------------------------

        candles = provider.get_candles(
            symbol=normalized_symbol,
            timeframe=mt5_timeframe,
            count=count,
        )

        if not candles:
            raise RuntimeError(
                "No MT5 candle data is available."
            )

        # --------------------------------------------------
        # INDICATORS
        # --------------------------------------------------

        ema20_series = (
            ChartIndicatorService
            .calculate_ema_series(
                candles,
                period=20,
            )
        )

        rsi14_series = (
            ChartIndicatorService
            .calculate_rsi_series(
                candles,
                period=14,
            )
        )

        adx14_series = (
            ChartIndicatorService
            .calculate_adx_series(
                candles,
                period=14,
            )
        )

        # --------------------------------------------------
        # ATR
        # --------------------------------------------------

        support_resistance_atr = (
            TechnicalIndicators
            .calculate_atr(
                candles,
                period=SUPPORT_RESISTANCE_ATR_PERIOD,
            )
        )

        support_resistance_tolerance = round(
            support_resistance_atr
            * SUPPORT_RESISTANCE_TOLERANCE_MULTIPLIER,
            6,
        )

        # --------------------------------------------------
        # EQH / EQL tolerance
        # --------------------------------------------------

        equal_high_low_tolerance = round(
            support_resistance_atr
            * EQUAL_HIGH_LOW_TOLERANCE_MULTIPLIER,
            6,
        )

        # --------------------------------------------------
        # SWINGS
        # --------------------------------------------------

        structure_lookback = 2

        swing_highs = (
            MarketStructureService
            .find_swing_highs(
                candles,
                lookback=structure_lookback,
            )
        )

        swing_lows = (
            MarketStructureService
            .find_swing_lows(
                candles,
                lookback=structure_lookback,
            )
        )

        # --------------------------------------------------
        # SUPPORT / RESISTANCE
        # --------------------------------------------------

        support_resistance = (
            MarketStructureService
            .detect_support_resistance_zones(
                swing_highs,
                swing_lows,
                tolerance=support_resistance_tolerance,
                min_touches=SUPPORT_RESISTANCE_MIN_TOUCHES,
            )
        )

        # --------------------------------------------------
        # EQUAL HIGHS / EQUAL LOWS
        # --------------------------------------------------

        equal_highs_lows = (
            MarketStructureService
            .detect_equal_highs_lows(
                swing_highs,
                swing_lows,
                tolerance=equal_high_low_tolerance,
                min_touches=EQUAL_HIGH_LOW_MIN_TOUCHES,
            )
        )

        # --------------------------------------------------
        # BOS
        # --------------------------------------------------

        latest_bos = (
            MarketStructureService
            .detect_bos(
                candles,
                swing_highs,
                swing_lows,
            )
        )

        # --------------------------------------------------
        # CHoCH
        # --------------------------------------------------

        latest_choch = (
            MarketStructureService
            .detect_choch(
                candles,
                swing_highs,
                swing_lows,
                latest_bos,
            )
        )

        # --------------------------------------------------
        # ORDER BLOCK
        # --------------------------------------------------

        latest_order_block = (
            MarketStructureService
            .detect_order_block(
                candles,
                latest_bos,
            )
        )

        # --------------------------------------------------
        # LIQUIDITY SWEEP
        # --------------------------------------------------

        latest_liquidity_sweep = (
            MarketStructureService
            .detect_liquidity_sweep(
                candles,
                swing_highs,
                swing_lows,
            )
        )

        # --------------------------------------------------
        # FAIR VALUE GAP
        # --------------------------------------------------

        latest_fvg = (
            MarketStructureService
            .detect_fvg(
                candles,
            )
        )

        # --------------------------------------------------
        # ENGULFING
        # --------------------------------------------------

        latest_engulfing = (
            MarketStructureService
            .detect_engulfing(
                candles,
            )
        )

        # --------------------------------------------------
        # DISPLACEMENT
        # --------------------------------------------------

        latest_displacement = (
            MarketStructureService
            .detect_displacement(
                candles,
                atr=support_resistance_atr,
                body_multiplier=(
                    DISPLACEMENT_BODY_ATR_MULTIPLIER
                ),
            )
        )

        # --------------------------------------------------
        # PREMIUM / DISCOUNT / EQUILIBRIUM
        # --------------------------------------------------

        latest_premium_discount = (
            MarketStructureService
            .detect_premium_discount(
                swing_highs,
                swing_lows,
            )
        )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        return {
            "symbol": normalized_symbol,
            "broker_symbol": candles[-1].symbol,
            "timeframe": normalized_timeframe,
            "count": len(candles),

            # ----------------------------------------------
            # OHLC
            # ----------------------------------------------

            "candles": [
                {
                    "time": int(
                        candle.timestamp.timestamp()
                    ),
                    "open": candle.open_price,
                    "high": candle.high_price,
                    "low": candle.low_price,
                    "close": candle.close_price,
                    "volume": candle.volume,
                }
                for candle in candles
            ],

            # ----------------------------------------------
            # INDICATORS
            # ----------------------------------------------

            "indicators": {
                "ema20": {
                    "period": 20,
                    "series": ema20_series,
                },
                "rsi14": {
                    "period": 14,
                    "series": rsi14_series,
                },
                "adx14": {
                    "period": 14,
                    "series": adx14_series,
                },
            },

            # ----------------------------------------------
            # MARKET STRUCTURE
            # ----------------------------------------------

            "market_structure": {

                "lookback": structure_lookback,

                # ------------------------------------------
                # SWINGS
                # ------------------------------------------

                "swing_highs": [
                    _serialize_swing_point(
                        point
                    )
                    for point in swing_highs
                ],

                "swing_lows": [
                    _serialize_swing_point(
                        point
                    )
                    for point in swing_lows
                ],

                # ------------------------------------------
                # SUPPORT / RESISTANCE
                # ------------------------------------------

                "support_resistance": {

                    "atr_period": (
                        SUPPORT_RESISTANCE_ATR_PERIOD
                    ),

                    "tolerance_multiplier": (
                        SUPPORT_RESISTANCE_TOLERANCE_MULTIPLIER
                    ),

                    "tolerance": (
                        support_resistance_tolerance
                    ),

                    "support_zones": (
                        support_resistance[
                            "support_zones"
                        ]
                    ),

                    "resistance_zones": (
                        support_resistance[
                            "resistance_zones"
                        ]
                    ),
                },

                # ------------------------------------------
                # EQUAL HIGHS / EQUAL LOWS
                # ------------------------------------------

                "equal_highs_lows": {

                    "tolerance_multiplier": (
                        EQUAL_HIGH_LOW_TOLERANCE_MULTIPLIER
                    ),

                    "tolerance": (
                        equal_high_low_tolerance
                    ),

                    "min_touches": (
                        EQUAL_HIGH_LOW_MIN_TOUCHES
                    ),

                    "equal_highs": (
                        equal_highs_lows[
                            "equal_highs"
                        ]
                    ),

                    "equal_lows": (
                        equal_highs_lows[
                            "equal_lows"
                        ]
                    ),
                },

                # ------------------------------------------
                # BOS
                # ------------------------------------------

                "bos": (
                    _serialize_structure_event(
                        latest_bos
                    )
                ),

                # ------------------------------------------
                # CHoCH
                # ------------------------------------------

                "choch": (
                    _serialize_structure_event(
                        latest_choch
                    )
                ),

                # ------------------------------------------
                # ORDER BLOCK
                # ------------------------------------------

                "order_block": (
                    _serialize_order_block(
                        latest_order_block
                    )
                ),

                # ------------------------------------------
                # LIQUIDITY SWEEP
                # ------------------------------------------

                "liquidity_sweep": (
                    _serialize_liquidity_sweep(
                        latest_liquidity_sweep
                    )
                ),

                # ------------------------------------------
                # FVG
                # ------------------------------------------

                "fvg": (
                    _serialize_fvg(
                        latest_fvg
                    )
                ),

                # ------------------------------------------
                # ENGULFING
                # ------------------------------------------

                "engulfing": (
                    _serialize_engulfing(
                        latest_engulfing
                    )
                ),

                # ------------------------------------------
                # DISPLACEMENT
                # ------------------------------------------

                "displacement": (
                    _serialize_displacement(
                        latest_displacement
                    )
                ),

                # ------------------------------------------
                # PREMIUM / DISCOUNT
                # ------------------------------------------

                "premium_discount": (
                    _serialize_premium_discount(
                        latest_premium_discount
                    )
                ),
            },
        }

    # ======================================================
    # ERROR HANDLING
    # ======================================================

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except RuntimeError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to retrieve MT5 "
                f"market candles: {error}"
            ),
        )

    finally:

        provider.disconnect()