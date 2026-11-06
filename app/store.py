import sqlite3
from contextlib import contextmanager
from pathlib import Path
from .config import settings

@contextmanager
def connect():
    path = settings.database_path
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    with connect() as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          email TEXT NOT NULL UNIQUE,
          password_hash TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS subscriptions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL REFERENCES users(id),
          token_hash TEXT NOT NULL UNIQUE,
          expires_at TEXT NOT NULL,
          active INTEGER NOT NULL DEFAULT 1,
          vless_uris_json TEXT NOT NULL DEFAULT '[]',
          created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_sub_user ON subscriptions(user_id);
        """)
        columns = {row["name"] for row in db.execute("PRAGMA table_info(subscriptions)")}
        if "vless_uris_json" not in columns:
            db.execute("ALTER TABLE subscriptions ADD COLUMN vless_uris_json TEXT NOT NULL DEFAULT '[]'")
