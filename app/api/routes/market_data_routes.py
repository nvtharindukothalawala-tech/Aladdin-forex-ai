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

from app.market.mt5_provider import (
    MT5DataProvider,
)

from app.services.chart_indicator_service import (
    ChartIndicatorService,
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

    Available instruments contain:

    - logical ALADDIN symbol
    - frontend display symbol
    - actual broker symbol
    - bid price
    - ask price
    - raw spread
    - spread in broker points
    - broker price precision
    - broker point size
    - MT5 tick timestamp
    - availability status

    Temporarily unavailable instruments remain
    visible in the response with:

    - available = False
    - market values = None
    - error message describing the data problem

    HTTP 503 is returned only when no valid quote
    can be retrieved from MT5.

    The endpoint:

    - reads MT5 market data
    - does not execute trades
    - does not modify positions
    - does not modify orders
    - does not change the DEMO execution safety switch
    """

    # Authentication is enforced by the dependency.
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

        # If MT5 failed to provide every quote,
        # treat the market-data service as unavailable.
        #
        # Preserve the first RuntimeError detail so the
        # existing API failure contract remains useful
        # for diagnostics and tests.
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
            "Supported values: M1, M5, M15, M30, H1, H4, D1, W1."
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

    It is intended for the ALADDIN V2 trading chart.

    The endpoint:

    - reads MT5 market data
    - does not execute trades
    - does not modify positions
    - does not modify orders
    - does not change the DEMO execution safety switch
    """

    # Authentication is enforced by the dependency.
    # The user object is intentionally retained here
    # so the endpoint follows Aladdin's authenticated
    # resource pattern.
    _ = current_user

    provider = MT5DataProvider()

    try:

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

        candles = provider.get_candles(
            symbol=normalized_symbol,
            timeframe=mt5_timeframe,
            count=count,
        )

        if not candles:
            raise RuntimeError(
                "No MT5 candle data is available."
            )

        ema20_series = (
            ChartIndicatorService.calculate_ema_series(
                candles,
                period=20,
            )
        )

        return {
            "symbol": normalized_symbol,
            "broker_symbol": candles[-1].symbol,
            "timeframe": normalized_timeframe,
            "count": len(candles),
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
            "indicators": {
                "ema20": {
                    "period": 20,
                    "series": ema20_series,
                },
            },
        }

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