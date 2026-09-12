"""
migrate_risk_reward_nullable.py

One-time SQLite migration that changes
trades.risk_reward from NOT NULL to nullable.

Existing trade data and MT5 indexes are preserved.

Author: Tharindu Kothalawala
Project: Aladdin
"""

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "aladdin.db"


def migrate():
    """
    Rebuild the trades table so that
    risk_reward can contain NULL.
    """

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )

    print(f"Database: {DATABASE_PATH}")

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        # --------------------------------------------------
        # Check current structure
        # --------------------------------------------------

        columns = cursor.execute(
            "PRAGMA table_info(trades)"
        ).fetchall()

        if not columns:
            raise RuntimeError(
                "The trades table does not exist."
            )

        risk_reward_column = next(
            (
                column
                for column in columns
                if column[1] == "risk_reward"
            ),
            None,
        )

        if risk_reward_column is None:
            raise RuntimeError(
                "risk_reward column was not found."
            )

        # PRAGMA table_info:
        # index 3 = NOT NULL flag
        is_not_null = risk_reward_column[3] == 1

        if not is_not_null:
            print(
                "risk_reward is already nullable."
            )
            return

        before_count = cursor.execute(
            "SELECT COUNT(*) FROM trades"
        ).fetchone()[0]

        print(
            f"Existing trade records: {before_count}"
        )

        print(
            "Changing risk_reward to nullable..."
        )

        # --------------------------------------------------
        # SQLite requires rebuilding the table
        # --------------------------------------------------

        connection.execute(
            "PRAGMA foreign_keys = OFF"
        )

        cursor.execute("BEGIN IMMEDIATE")

        # Remove an unfinished temporary table
        # only if a previous migration was interrupted.
        cursor.execute(
            "DROP TABLE IF EXISTS trades_new"
        )

        # --------------------------------------------------
        # Create replacement table
        # --------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE trades_new (
                id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                symbol VARCHAR NOT NULL,
                direction VARCHAR NOT NULL,
                result VARCHAR NOT NULL,
                profit_loss FLOAT NOT NULL,

                risk_reward FLOAT,

                created_at DATETIME,

                source VARCHAR DEFAULT 'ALADDIN',

                mt5_deal_ticket INTEGER,
                mt5_order_ticket INTEGER,
                mt5_position_id INTEGER,

                close_price FLOAT,

                commission FLOAT DEFAULT 0.0,
                swap FLOAT DEFAULT 0.0,
                fee FLOAT DEFAULT 0.0,

                closed_at DATETIME,

                is_aladdin_trade INTEGER DEFAULT 0,

                PRIMARY KEY (id),

                FOREIGN KEY(user_id)
                    REFERENCES users (id)
            )
            """
        )

        # --------------------------------------------------
        # Copy all existing records
        # --------------------------------------------------

        cursor.execute(
            """
            INSERT INTO trades_new (
                id,
                user_id,
                symbol,
                direction,
                result,
                profit_loss,
                risk_reward,
                created_at,
                source,
                mt5_deal_ticket,
                mt5_order_ticket,
                mt5_position_id,
                close_price,
                commission,
                swap,
                fee,
                closed_at,
                is_aladdin_trade
            )
            SELECT
                id,
                user_id,
                symbol,
                direction,
                result,
                profit_loss,
                risk_reward,
                created_at,
                source,
                mt5_deal_ticket,
                mt5_order_ticket,
                mt5_position_id,
                close_price,
                commission,
                swap,
                fee,
                closed_at,
                is_aladdin_trade
            FROM trades
            """
        )

        copied_count = cursor.execute(
            "SELECT COUNT(*) FROM trades_new"
        ).fetchone()[0]

        if copied_count != before_count:
            raise RuntimeError(
                "Migration validation failed: "
                f"expected {before_count} rows, "
                f"copied {copied_count}."
            )

        # --------------------------------------------------
        # Replace old table
        # --------------------------------------------------

        cursor.execute(
            "DROP TABLE trades"
        )

        cursor.execute(
            """
            ALTER TABLE trades_new
            RENAME TO trades
            """
        )

        # --------------------------------------------------
        # Restore indexes
        # --------------------------------------------------

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            ix_trades_id
            ON trades(id)
            """
        )

        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            ux_trades_mt5_deal_ticket
            ON trades(mt5_deal_ticket)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            ix_trades_mt5_position_id
            ON trades(mt5_position_id)
            """
        )

        # --------------------------------------------------
        # Final validation
        # --------------------------------------------------

        after_count = cursor.execute(
            "SELECT COUNT(*) FROM trades"
        ).fetchone()[0]

        if after_count != before_count:
            raise RuntimeError(
                "Final row-count validation failed."
            )

        final_columns = cursor.execute(
            "PRAGMA table_info(trades)"
        ).fetchall()

        final_rr = next(
            column
            for column in final_columns
            if column[1] == "risk_reward"
        )

        if final_rr[3] != 0:
            raise RuntimeError(
                "risk_reward is still NOT NULL."
            )

        connection.commit()

        print(
            "Migration completed successfully."
        )

        print(
            f"Trade records preserved: {after_count}"
        )

        print(
            "risk_reward is now nullable."
        )

        print(
            "MT5 duplicate-protection index restored."
        )

        print(
            "MT5 position index restored."
        )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        connection.close()


if __name__ == "__main__":
    migrate()