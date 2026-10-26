"""The phylactery — where a minion's findings and the soul ledger survive its death."""
from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass


SCHEMA = """
CREATE TABLE IF NOT EXISTS findings (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    minion   TEXT NOT NULL,
    target   TEXT,
    kind     TEXT NOT NULL,
    detail   TEXT,
    ts       REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS ledger (
    minion   TEXT NOT NULL,
    essence  INTEGER NOT NULL,
    spent    INTEGER NOT NULL DEFAULT 0,
    raised   REAL NOT NULL
);
"""


@dataclass
class Finding:
    minion: str
    target: str | None
    kind: str
    detail: str


class Phylactery:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # --- findings -------------------------------------------------------
    def record(self, f: Finding) -> None:
        self.conn.execute(
            "INSERT INTO findings (minion, target, kind, detail, ts) VALUES (?,?,?,?,?)",
            (f.minion, f.target, f.kind, f.detail, time.time()),
        )
        self.conn.commit()

    def findings(self) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM findings ORDER BY ts DESC"
        ).fetchall()

    # --- soul ledger ----------------------------------------------------
    def grant_essence(self, minion: str, essence: int) -> None:
        self.conn.execute(
            "INSERT INTO ledger (minion, essence, spent, raised) VALUES (?,?,0,?)",
            (minion, essence, time.time()),
        )
        self.conn.commit()

    def spend(self, minion: str, amount: int = 1) -> None:
        self.conn.execute(
            "UPDATE ledger SET spent = spent + ? WHERE minion = ?",
            (amount, minion),
        )
        self.conn.commit()

    def banish_all(self) -> None:
        self.conn.executescript("DELETE FROM findings; DELETE FROM ledger;")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
