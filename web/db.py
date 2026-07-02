"""IV Consulting database layer.

Supports both SQLite (local dev) and PostgreSQL (production).
Set DATABASE_URL env var for Postgres, otherwise uses local SQLite.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DATABASE_URL = os.environ.get("DATABASE_URL", "")
_USE_PG = DATABASE_URL.startswith("postgres")

if _USE_PG:
    import psycopg2
    import psycopg2.extras


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id() -> str:
    return uuid.uuid4().hex[:12]


class PgConnWrapper:
    """Wraps psycopg2 connection to provide SQLite-like interface."""

    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql: str, params: tuple = ()) -> "PgCursorWrapper":
        sql = sql.replace("?", "%s")
        cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        return PgCursorWrapper(cur)

    def executescript(self, sql: str) -> None:
        cur = self._conn.cursor()
        cur.execute(sql)

    def commit(self) -> None:
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


class PgCursorWrapper:
    def __init__(self, cur):
        self._cur = cur

    def fetchone(self):
        row = self._cur.fetchone()
        return PgRow(dict(row)) if row else None

    def fetchall(self):
        return [PgRow(dict(r)) for r in self._cur.fetchall()]


class PgRow(dict):
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


def get_conn():
    """Return a DB connection (SQLite or Postgres)."""
    if _USE_PG:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        return PgConnWrapper(conn)
    else:
        db_path = Path(os.environ.get("DATABASE_PATH",
            str(Path(__file__).resolve().parent.parent / "data" / "experiments.db")))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn


# ── Schema ──────────────────────────────────────────────────────

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'draft',
    priority TEXT DEFAULT 'medium',
    tags TEXT DEFAULT '[]',
    meta TEXT DEFAULT '{}',
    parent_id TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS edges (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    rel_type TEXT NOT NULL,
    meta TEXT DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS aeo_evidence (
    id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    engine TEXT DEFAULT 'chatgpt',
    cited_url TEXT DEFAULT '',
    brand_mentioned INTEGER DEFAULT 0,
    snippet TEXT DEFAULT '',
    screenshot_path TEXT DEFAULT '',
    checked_at TEXT NOT NULL,
    meta TEXT DEFAULT '{}'
);
"""

_INDEXES_SQL = """
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);
CREATE INDEX IF NOT EXISTS idx_nodes_status ON nodes(status);
CREATE INDEX IF NOT EXISTS idx_nodes_parent ON nodes(parent_id);
CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
CREATE INDEX IF NOT EXISTS idx_aeo_query ON aeo_evidence(query);
"""


def init_db() -> None:
    """Create all tables if they don't exist."""
    conn = get_conn()
    conn.executescript(_SCHEMA_SQL)
    conn.commit()
    for line in _INDEXES_SQL.strip().split(";"):
        line = line.strip()
        if line:
            try:
                conn.execute(line)
            except Exception:
                pass
    conn.commit()
    conn.close()


# ── Node CRUD ───────────────────────────────────────────────────

def create_node(node_type: str, title: str, **kwargs) -> dict:
    conn = get_conn()
    nid = _id()
    now = _now()
    conn.execute(
        "INSERT INTO nodes (id, type, title, description, status, priority, tags, meta, parent_id, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (nid, node_type, title,
         kwargs.get("description", ""),
         kwargs.get("status", "draft"),
         kwargs.get("priority", "medium"),
         json.dumps(kwargs.get("tags", []), ensure_ascii=False),
         json.dumps(kwargs.get("meta", {}), ensure_ascii=False),
         kwargs.get("parent_id", ""),
         now, now),
    )
    conn.commit()
    conn.close()
    return {"id": nid, "type": node_type, "title": title, "status": kwargs.get("status", "draft")}


def list_nodes(node_type: str | None = None, status: str | None = None) -> list[dict]:
    conn = get_conn()
    sql = "SELECT * FROM nodes"
    params: list = []
    conditions = []
    if node_type:
        conditions.append("type = ?")
        params.append(node_type)
    if status:
        conditions.append("status = ?")
        params.append(status)
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY created_at DESC"
    rows = conn.execute(sql, tuple(params)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_node(nid: str) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM nodes WHERE id=?", (nid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_node(nid: str, **kwargs) -> dict | None:
    conn = get_conn()
    sets = []
    params = []
    for key in ("title", "description", "status", "priority", "parent_id"):
        if key in kwargs:
            sets.append(f"{key} = ?")
            params.append(kwargs[key])
    if "tags" in kwargs:
        sets.append("tags = ?")
        params.append(json.dumps(kwargs["tags"], ensure_ascii=False))
    if "meta" in kwargs:
        sets.append("meta = ?")
        params.append(json.dumps(kwargs["meta"], ensure_ascii=False))
    sets.append("updated_at = ?")
    params.append(_now())
    params.append(nid)
    conn.execute(f"UPDATE nodes SET {', '.join(sets)} WHERE id = ?", tuple(params))
    conn.commit()
    row = conn.execute("SELECT * FROM nodes WHERE id=?", (nid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_node(nid: str) -> None:
    conn = get_conn()
    conn.execute("DELETE FROM nodes WHERE id=?", (nid,))
    conn.execute("DELETE FROM edges WHERE source_id=? OR target_id=?", (nid, nid))
    conn.commit()
    conn.close()


# ── Edge CRUD ───────────────────────────────────────────────────

def create_edge(source_id: str, target_id: str, rel_type: str, meta: dict | None = None) -> dict:
    conn = get_conn()
    eid = _id()
    now = _now()
    conn.execute(
        "INSERT INTO edges (id, source_id, target_id, rel_type, meta, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (eid, source_id, target_id, rel_type, json.dumps(meta or {}, ensure_ascii=False), now),
    )
    conn.commit()
    conn.close()
    return {"id": eid, "source_id": source_id, "target_id": target_id, "rel_type": rel_type}


def get_edges(node_id: str) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM edges WHERE source_id=? OR target_id=?", (node_id, node_id)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── AEO Evidence ────────────────────────────────────────────────

def add_evidence(query: str, **kwargs) -> dict:
    conn = get_conn()
    eid = _id()
    conn.execute(
        "INSERT INTO aeo_evidence (id, query, engine, cited_url, brand_mentioned, snippet, screenshot_path, checked_at, meta) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (eid, query,
         kwargs.get("engine", "chatgpt"),
         kwargs.get("cited_url", ""),
         kwargs.get("brand_mentioned", 0),
         kwargs.get("snippet", ""),
         kwargs.get("screenshot_path", ""),
         _now(),
         json.dumps(kwargs.get("meta", {}), ensure_ascii=False)),
    )
    conn.commit()
    conn.close()
    return {"id": eid, "query": query}


def list_evidence(limit: int = 100) -> list[dict]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM aeo_evidence ORDER BY checked_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
