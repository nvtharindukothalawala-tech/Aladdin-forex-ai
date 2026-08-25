"""
instrument_config.py

Central configuration for Aladdin supported trading instruments.

Author: Tharindu Kothalawala
Project: Aladdin
"""


INSTRUMENTS = {
    "EURUSD": {
        "display_symbol": "EUR/USD",
        "mt5_symbols": [
            "EURUSD",
            "EURUSDm",
            "EURUSD.",
        ],
        "asset_type": "FOREX",
        "pip_size": 0.0001,
        "pip_value": 10.0,
        "price_decimals": 5,
    },

    "GBPUSD": {
        "display_symbol": "GBP/USD",
        "mt5_symbols": [
            "GBPUSD",
            "GBPUSDm",
            "GBPUSD.",
        ],
        "asset_type": "FOREX",
        "pip_size": 0.0001,
        "pip_value": 10.0,
        "price_decimals": 5,
    },

    "AUDUSD": {
        "display_symbol": "AUD/USD",
        "mt5_symbols": [
            "AUDUSD",
            "AUDUSDm",
            "AUDUSD.",
        ],
        "asset_type": "FOREX",
        "pip_size": 0.0001,
        "pip_value": 10.0,
        "price_decimals": 5,
    },

    "NZDUSD": {
        "display_symbol": "NZD/USD",
        "mt5_symbols": [
            "NZDUSD",
            "NZDUSDm",
            "NZDUSD.",
        ],
        "asset_type": "FOREX",
        "pip_size": 0.0001,
        "pip_value": 10.0,
        "price_decimals": 5,
    },

    "USDCAD": {
        "display_symbol": "USD/CAD",
        "mt5_symbols": [
            "USDCAD",
            "USDCADm",
            "USDCAD.",
        ],
        "asset_type": "FOREX",
        "pip_size": 0.0001,
        "pip_value": 10.0,
        "price_decimals": 5,
    },

    "USDCHF": {
        "display_symbol": "USD/CHF",
        "mt5_symbols": [
            "USDCHF",
            "USDCHFm",
            "USDCHF.",
        ],
        "asset_type": "FOREX",
        "pip_size": 0.0001,
        "pip_value": 10.0,
        "price_decimals": 5,
    },

    "USDJPY": {
        "display_symbol": "USD/JPY",
        "mt5_symbols": [
            "USDJPY",
            "USDJPYm",
            "USDJPY.",
        ],
        "asset_type": "FOREX",
        "pip_size": 0.01,
        "pip_value": 10.0,
        "price_decimals": 3,
    },

    "XAUUSD": {
        "display_symbol": "XAU/USD",
        "mt5_symbols": [
            "XAUUSD",
            "XAUUSDm",
            "XAUUSD.",
            "GOLD",
            "GOLDm",
        ],
        "asset_type": "METAL",
        "pip_size": 0.01,

        # Project calculation convention.
        # The broker's actual MT5 contract specification
        # should be used before real-money execution.
        "pip_value": 1.0,

        "price_decimals": 2,
    },
}


def normalize_symbol(symbol: str) -> str:
    """
    Convert display/MT5-style symbols into
    the internal symbol key.

    Examples:
        EUR/USD -> EURUSD
        EURUSD  -> EURUSD
        XAU/USD -> XAUUSD
        GOLD    -> XAUUSD
    """

    if not symbol:
        raise ValueError(
            "Trading symbol cannot be empty."
        )

    normalized = (
        symbol
        .strip()
        .upper()
        .replace("/", "")
        .replace("_", "")
        .replace("-", "")
    )

    if normalized in {
        "GOLD",
        "GOLDM",
        "XAUUSD",
        "XAUUSDM",
    }:
        return "XAUUSD"

    for key, config in INSTRUMENTS.items():

        if normalized == key:
            return key

        for mt5_symbol in config["mt5_symbols"]:

            candidate = (
                mt5_symbol
                .upper()
                .replace("/", "")
                .replace("_", "")
                .replace("-", "")
            )

            if normalized == candidate:
                return key

    raise ValueError(
        f"Unsupported trading symbol: {symbol}"
    )


def get_instrument(symbol: str) -> dict:
    """
    Return configuration for a supported instrument.
    """

    key = normalize_symbol(symbol)

    return INSTRUMENTS[key]


def get_display_symbol(symbol: str) -> str:
    """
    Return frontend display symbol.
    """

    return get_instrument(
        symbol
    )["display_symbol"]


def get_pip_size(symbol: str) -> float:
    """
    Return configured pip size.
    """

    return float(
        get_instrument(
            symbol
        )["pip_size"]
    )


def get_pip_value(symbol: str) -> float:
    """
    Return configured pip value for
    one standard lot.
    """

    return float(
        get_instrument(
            symbol
        )["pip_value"]
    )


def get_price_decimals(symbol: str) -> int:
    """
    Return normal display precision.
    """

    return int(
        get_instrument(
            symbol
        )["price_decimals"]
    )