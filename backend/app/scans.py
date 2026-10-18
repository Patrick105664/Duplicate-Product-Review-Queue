from datetime import datetime, timezone
import sqlite3
from app.db import now


def start_scan_run(conn: sqlite3.Connection, source: str = "current-catalogue") -> int:
    """Record the start of a duplicate detection scan run."""
    ts = now()
    cur = conn.execute(
        """
        INSERT INTO scan_runs (started_at, source, status)
        VALUES (?, ?, 'running')
        """,
        (ts, source),
    )
    conn.commit()
    return cur.lastrowid


def finish_scan_run(
    conn: sqlite3.Connection,
    scan_id: int,
    *,
    products_count: int,
    pairs_found: int,
    new_pairs: int,
    status: str = "completed",
    error: str | None = None,
) -> None:
    """Record completion of a scan run, computing duration."""
    if status not in ("completed", "failed"):
        raise ValueError(f"Invalid scan status: {status!r}")

    row = conn.execute(
        "SELECT started_at FROM scan_runs WHERE scan_id = ?", (scan_id,)
    ).fetchone()
    if row is None:
        raise KeyError(f"Unknown scan_id: {scan_id}")

    finish_ts = now()
    start_dt = datetime.fromisoformat(row["started_at"])
    finish_dt = datetime.fromisoformat(finish_ts)
    duration_seconds = max(0.0, (finish_dt - start_dt).total_seconds())

    conn.execute(
        """
        UPDATE scan_runs
        SET finished_at = ?,
            products_count = ?,
            pairs_found = ?,
            new_pairs = ?,
            status = ?,
            duration_seconds = ?,
            error = ?
        WHERE scan_id = ?
        """,
        (
            finish_ts,
            products_count,
            pairs_found,
            new_pairs,
            status,
            duration_seconds,
            error,
            scan_id,
        ),
    )
    conn.commit()


def list_scan_runs(conn: sqlite3.Connection, limit: int = 50) -> list[dict]:
    """Return recent scan runs, newest first."""
    rows = conn.execute(
        "SELECT * FROM scan_runs ORDER BY scan_id DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(r) for r in rows]


def get_scan_run(conn: sqlite3.Connection, scan_id: int) -> dict | None:
    """Return a single scan run by ID, or None."""
    row = conn.execute(
        "SELECT * FROM scan_runs WHERE scan_id = ?", (scan_id,)
    ).fetchone()
    if row is None:
        return None
    return dict(row)


def scans_this_month(conn: sqlite3.Connection) -> int:
    """Count of scan runs started in the current calendar month (UTC)."""
    now_utc = datetime.now(timezone.utc)
    start_of_month = datetime(now_utc.year, now_utc.month, 1, 0, 0, 0, tzinfo=timezone.utc).isoformat()
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM scan_runs WHERE started_at >= ?",
        (start_of_month,),
    ).fetchone()
    return row["c"]
