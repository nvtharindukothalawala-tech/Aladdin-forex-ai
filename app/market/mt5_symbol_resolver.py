"""
mt5_symbol_resolver.py

Resolves Aladdin symbols to the actual
MetaTrader 5 broker symbol.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from app.config.instrument_config import (
    INSTRUMENTS,
    normalize_symbol,
)


class MT5SymbolResolver:
    """
    Resolve logical Aladdin symbols to
    broker-provided MT5 symbols.
    """

    @staticmethod
    def resolve(
        symbol: str,
        mt5_module,
    ) -> str:
        """
        Find the first available MT5 symbol.
        """

        internal_symbol = (
            normalize_symbol(
                symbol
            )
        )

        candidates = (
            INSTRUMENTS[
                internal_symbol
            ]["mt5_symbols"]
        )

        for candidate in candidates:

            info = (
                mt5_module.symbol_info(
                    candidate
                )
            )

            if info is not None:
                return candidate

        # Fallback: search all broker symbols.
        all_symbols = (
            mt5_module.symbols_get()
        )

        if all_symbols:

            for broker_symbol in all_symbols:

                name = (
                    broker_symbol.name
                    .upper()
                )

                clean_name = (
                    name
                    .replace("/", "")
                    .replace("_", "")
                    .replace("-", "")
                )

                if internal_symbol == "XAUUSD":

                    if (
                        "XAUUSD"
                        in clean_name
                        or clean_name.startswith(
                            "GOLD"
                        )
                    ):
                        return (
                            broker_symbol.name
                        )

                elif clean_name.startswith(
                    internal_symbol
                ):
                    return (
                        broker_symbol.name
                    )

        raise ValueError(
            f"MT5 symbol for {symbol} "
            "was not found. "
            "Open MT5 Market Watch and "
            "make sure the instrument is visible."
        )