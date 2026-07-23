import sqlite3
import os
import time
from dataclasses import dataclass
from typing import Optional

from assistant.config import cfg

_SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    ts REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS entities (
    kind TEXT NOT NULL,
    name TEXT NOT NULL,
    value TEXT NOT NULL,
    ts REAL NOT NULL,
    PRIMARY KEY (kind, name)
);
CREATE TABLE IF NOT EXISTS commands (
    command TEXT PRIMARY KEY,
    count INTEGER NOT NULL DEFAULT 1,
    last_ts REAL NOT NULL
);
"""


class Memory:
    def __init__(self, path: str = cfg.db_path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    def add_message(self, role: str, content: str) -> None:
        self.conn.execute(
            "INSERT INTO history (role, content, ts) VALUES (?, ?, ?)",
            (role, content, time.time()),
        )
        self.conn.commit()

    def recent_history(self, limit: int = 10) -> list[tuple[str, str]]:
        rows = self.conn.execute(
            "SELECT role, content FROM history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return list(reversed(rows))

    def remember_entity(self, kind: str, name: str, value: str) -> None:
        self.conn.execute(
            "INSERT INTO entities (kind, name, value, ts) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(kind, name) DO UPDATE SET value=excluded.value, ts=excluded.ts",
            (kind, name, value, time.time()),
        )
        self.conn.commit()

    def get_entity(self, kind: str, name: str) -> Optional[str]:
        row = self.conn.execute(
            "SELECT value FROM entities WHERE kind=? AND name=?", (kind, name)
        ).fetchone()
        return row[0] if row else None

    def last_entity(self, kind: str) -> Optional[str]:
        row = self.conn.execute(
            "SELECT value FROM entities WHERE kind=? ORDER BY ts DESC LIMIT 1", (kind,)
        ).fetchone()
        return row[0] if row else None

    def track_command(self, command: str) -> None:
        self.conn.execute(
            "INSERT INTO commands (command, count, last_ts) VALUES (?, 1, ?) "
            "ON CONFLICT(command) DO UPDATE SET count=count+1, last_ts=excluded.last_ts",
            (command, time.time()),
        )
        self.conn.commit()


memory = Memory()
