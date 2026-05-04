import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "stock_portfolio.db"


class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                name TEXT NOT NULL,
                trade_time TEXT NOT NULL,
                side TEXT NOT NULL CHECK(side IN ('BUY', 'SELL')),
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                currency TEXT NOT NULL CHECK(currency IN ('USD', 'TWD')),
                fee REAL NOT NULL DEFAULT 0,
                tax REAL NOT NULL DEFAULT 0,
                note TEXT DEFAULT ''
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS market_prices (
                symbol TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                currency TEXT NOT NULL CHECK(currency IN ('USD', 'TWD')),
                current_price REAL NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def seed_demo_data(self):
        cur = self.conn.cursor()
        count = cur.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
        if count > 0:
            return

        demo_trades = [
            ("AAPL", "Apple", "2026-01-10 09:30", "BUY", 20, 180, "USD", 1, 0, "長期投資"),
            ("AAPL", "Apple", "2026-02-10 10:00", "BUY", 10, 190, "USD", 1, 0, "加碼"),
            ("AAPL", "Apple", "2026-03-01 13:30", "SELL", 8, 210, "USD", 1, 2, "部分獲利了結"),
            ("TSLA", "Tesla", "2026-01-15 11:00", "BUY", 5, 220, "USD", 1, 0, "波段"),
            ("2330", "TSMC", "2026-01-18 09:05", "BUY", 100, 820, "TWD", 20, 0, "台股核心"),
            ("2330", "TSMC", "2026-02-15 10:20", "SELL", 30, 900, "TWD", 20, 81, "調節"),
        ]
        cur.executemany(
            """
            INSERT INTO trades
            (symbol, name, trade_time, side, quantity, price, currency, fee, tax, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            demo_trades,
        )
        demo_prices = [
            ("AAPL", "Apple", "USD", 205, "2026-05-01 12:00"),
            ("TSLA", "Tesla", "USD", 240, "2026-05-01 12:00"),
            ("2330", "TSMC", "TWD", 880, "2026-05-01 12:00"),
        ]
        cur.executemany(
            """
            INSERT INTO market_prices(symbol, name, currency, current_price, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            demo_prices,
        )
        self.conn.commit()

    def fetch_trades(self):
        return self.conn.execute("SELECT * FROM trades ORDER BY trade_time DESC").fetchall()

    def insert_trade(self, row):
        self.conn.execute(
            """
            INSERT INTO trades(symbol, name, trade_time, side, quantity, price, currency, fee, tax, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            row,
        )
        self.conn.commit()

    def update_trade(self, trade_id, row):
        self.conn.execute(
            """
            UPDATE trades
            SET symbol=?, name=?, trade_time=?, side=?, quantity=?, price=?, currency=?, fee=?, tax=?, note=?
            WHERE id=?
            """,
            (*row, trade_id),
        )
        self.conn.commit()

    def delete_trade(self, trade_id):
        self.conn.execute("DELETE FROM trades WHERE id=?", (trade_id,))
        self.conn.commit()

    def fetch_prices(self):
        return self.conn.execute("SELECT * FROM market_prices ORDER BY symbol").fetchall()

    def upsert_price(self, symbol, name, currency, current_price, updated_at):
        self.conn.execute(
            """
            INSERT INTO market_prices(symbol, name, currency, current_price, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(symbol)
            DO UPDATE SET
                name=excluded.name,
                currency=excluded.currency,
                current_price=excluded.current_price,
                updated_at=excluded.updated_at
            """,
            (symbol, name, currency, current_price, updated_at),
        )
        self.conn.commit()
