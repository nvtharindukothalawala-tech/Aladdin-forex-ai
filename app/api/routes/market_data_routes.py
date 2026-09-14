"""
market_data_routes.py

Authenticated read-only MT5 market-data endpoints
for the Aladdin V2 Trading Terminal.

Provides real OHLC candle data from the connected
MetaTrader 5 terminal for chart visualization.

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

from app.market.mt5_provider import (
    MT5DataProvider,
)


router = APIRouter(
    prefix="/market-data",
    tags=["Market Data"],
)


# ==========================================================
# SUPPORTED SYMBOLS
# ==========================================================

SUPPORTED_SYMBOLS = {
    "EURUSD",
    "GBPUSD",
    "AUDUSD",
    "NZDUSD",
    "USDCAD",
    "USDCHF",
    "USDJPY",
    "XAUUSD",
}


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
    Convert a frontend timeframe name into
    the corresponding MetaTrader 5 constant.

    ALADDIN V2 currently supports:

        M15 - Entry timeframe
        H1  - Primary timeframe
        H4  - Higher timeframe
    """

    mt5_module = provider._require_mt5()

    normalized = (
        timeframe
        .strip()
        .upper()
    )

    timeframe_map = {
        "M15": mt5_module.TIMEFRAME_M15,
        "H1": mt5_module.TIMEFRAME_H1,
        "H4": mt5_module.TIMEFRAME_H4,
    }

    if normalized not in timeframe_map:
        raise ValueError(
            "Unsupported timeframe. "
            "Supported timeframes are M15, H1, and H4."
        )

    return (
        normalized,
        timeframe_map[normalized],
    )


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
            "Supported values: M15, H1, H4."
        ),
    ),
    count: int = Query(
        default=300,
        ge=50,
        le=1000,
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