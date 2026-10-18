import sqlite3
from app.db import now, get_suggestion


def flag_pair(
    conn: sqlite3.Connection,
    key: str,
    reviewer: str,
    note: str | None = None,
) -> dict:
    """Flag a suggestion for further review without creating a decision."""
    if get_suggestion(conn, key) is None:
        raise KeyError(f"No suggestion for pair_key: {key!r}")

    ts = now()
    conn.execute(
        """
        INSERT INTO pair_flags (pair_key, reviewer, note, flagged_at)
        VALUES (?, ?, ?, ?)
        """,
        (key, reviewer, note, ts),
    )
    conn.commit()
    return {
        "pair_key": key,
        "reviewer": reviewer,
        "note": note,
        "flagged_at": ts,
    }


def get_latest_flag(conn: sqlite3.Connection, key: str) -> dict | None:
    """Get the latest flag record for a pair_key, or None."""
    row = conn.execute(
        """
        SELECT pair_key, reviewer, note, flagged_at
        FROM pair_flags
        WHERE pair_key = ?
        ORDER BY flag_id DESC
        LIMIT 1
        """,
        (key,),
    ).fetchone()
    if row is None:
        return None
    return dict(row)


def list_flagged_keys(conn: sqlite3.Connection) -> set[str]:
    """Return set of pair_keys that have a flag and no recorded decision."""
    sql = """
        SELECT DISTINCT pf.pair_key
        FROM pair_flags pf
        LEFT JOIN decisions d ON d.pair_key = pf.pair_key
        WHERE d.pair_key IS NULL
    """
    rows = conn.execute(sql).fetchall()
    return {r["pair_key"] for r in rows}
