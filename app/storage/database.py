import sqlite3
import os
from contextlib import contextmanager

DATA_DIR = os.getenv("DATA_DIR", "data")
DB_PATH = os.path.join(DATA_DIR, "bot.db")

def get_connection() -> sqlite3.Connection:
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn

@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_database():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT,
                message_id INTEGER,
                signal_index INTEGER,
                time TEXT NOT NULL,
                color TEXT NOT NULL,
                number INTEGER NOT NULL,
                date TEXT NOT NULL,
                cancelled INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT NOT NULL,
                status TEXT NOT NULL,
                attempts INTEGER DEFAULT 0,
                saved_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bank_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                initial_bank REAL NOT NULL,
                current_bank REAL NOT NULL,
                daily_goal_percent REAL NOT NULL,
                bet_percent REAL NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                start_bank REAL NOT NULL,
                profit REAL DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                cancelled INTEGER DEFAULT 0,
                goal_reached INTEGER DEFAULT 0,
                goal_reached_at TEXT
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_date ON signals(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_executions_saved_at ON executions(saved_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date)")

init_database()
