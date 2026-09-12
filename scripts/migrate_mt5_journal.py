"""
migrate_mt5_journal.py

One-time SQLite migration for adding
MT5 trade-history fields to the Aladdin
trade journal.

This migration:
- Keeps all existing trade records
- Adds MT5 broker identifiers
- Adds closed-trade information
- Adds duplicate protection
- Can safely be run more than once

Author: Tharindu Kothalawala
Project: Aladdin
"""

import sqlite3
from pathlib import Path


# ======================================================
# DATABASE LOCATION
# ======================================================

PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent
)

DATABASE_PATH = (
    PROJECT_ROOT / "aladdin.db"
)


# ======================================================
# NEW TRADE COLUMNS
# ======================================================

NEW_COLUMNS = {
    "source": (
        "VARCHAR DEFAULT 'ALADDIN'"
    ),
    "mt5_deal_ticket": (
        "INTEGER"
    ),
    "mt5_order_ticket": (
        "INTEGER"
    ),
    "mt5_position_id": (
        "INTEGER"
    ),
    "close_price": (
        "FLOAT"
    ),
    "commission": (
        "FLOAT DEFAULT 0.0"
    ),
    "swap": (
        "FLOAT DEFAULT 0.0"
    ),
    "fee": (
        "FLOAT DEFAULT 0.0"
    ),
    "closed_at": (
        "DATETIME"
    ),
    "is_aladdin_trade": (
        "INTEGER DEFAULT 0"
    ),
}


# ======================================================
# MIGRATION
# ======================================================

def migrate():
    """
    Add MT5 journal fields to the existing
    SQLite trades table.

    Existing columns and records are preserved.
    """

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )

    print(
        f"Database: {DATABASE_PATH}"
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    try:
        cursor = connection.cursor()

        # ==============================================
        # CHECK TRADES TABLE
        # ==============================================

        table_exists = cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'trades'
            """
        ).fetchone()

        if table_exists is None:
            raise RuntimeError(
                "The 'trades' table does not exist."
            )

        # ==============================================
        # READ EXISTING COLUMNS
        # ==============================================

        table_info = cursor.execute(
            "PRAGMA table_info(trades)"
        ).fetchall()

        existing_columns = {
            row[1]
            for row in table_info
        }

        print(
            "\nExisting columns:"
        )

        for column in sorted(
            existing_columns
        ):
            print(
                f"  - {column}"
            )

        # ==============================================
        # ADD MISSING COLUMNS
        # ==============================================

        print(
            "\nApplying migration..."
        )

        added_columns = []

        for (
            column_name,
            column_definition,
        ) in NEW_COLUMNS.items():

            if (
                column_name
                in existing_columns
            ):
                print(
                    f"SKIP: {column_name} "
                    "already exists."
                )

                continue

            sql = (
                "ALTER TABLE trades "
                f"ADD COLUMN {column_name} "
                f"{column_definition}"
            )

            cursor.execute(sql)

            added_columns.append(
                column_name
            )

            print(
                f"ADDED: {column_name}"
            )

        # ==============================================
        # DUPLICATE PROTECTION
        # ==============================================
        #
        # MT5 deal tickets uniquely identify broker
        # deals.
        #
        # SQLite allows multiple NULL values inside
        # a UNIQUE index, so existing non-MT5 trades
        # remain valid.
        # ==============================================

        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            ux_trades_mt5_deal_ticket
            ON trades(mt5_deal_ticket)
            """
        )

        print(
            "READY: MT5 deal-ticket "
            "duplicate protection."
        )

        # ==============================================
        # POSITION LOOKUP INDEX
        # ==============================================

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            ix_trades_mt5_position_id
            ON trades(mt5_position_id)
            """
        )

        print(
            "READY: MT5 position lookup index."
        )

        # ==============================================
        # COMMIT
        # ==============================================

        connection.commit()

        # ==============================================
        # VERIFY FINAL STRUCTURE
        # ==============================================

        final_columns = cursor.execute(
            "PRAGMA table_info(trades)"
        ).fetchall()

        print(
            "\nFinal trades table:"
        )

        for column in final_columns:
            print(
                f"  - {column[1]} "
                f"({column[2]})"
            )

        trade_count = cursor.execute(
            "SELECT COUNT(*) FROM trades"
        ).fetchone()[0]

        print(
            "\nMigration completed successfully."
        )

        print(
            f"Existing trade records preserved: "
            f"{trade_count}"
        )

        if added_columns:
            print(
                "New columns added: "
                + ", ".join(
                    added_columns
                )
            )
        else:
            print(
                "No new columns were required."
            )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ======================================================
# RUN
# ======================================================

if __name__ == "__main__":
    migrate()