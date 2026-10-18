import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

_SCHEMA = Path(__file__).with_name("schema.sql")
_DEFAULT_DB = os.getenv("REVIEW_DB_PATH", "data/review.db")


def now() -> str:
    """ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def pair_key(a: str, b: str) -> str:
    """Canonical key for a product pair (order-independent)."""
    ids = sorted([a, b])
    return f"{ids[0]}|{ids[1]}"


def get_conn(path: str | None = None) -> sqlite3.Connection:
    """Return a connection with Row factory and foreign keys enabled."""
    db_path = path or _DEFAULT_DB
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Run schema.sql and apply migrations. Safe to call repeatedly."""
    sql = _SCHEMA.read_text()
    conn.executescript(sql)
    for table in ("decisions", "decision_log"):
        cols = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        if "reviewer_id" not in cols:
            conn.execute(
                f"ALTER TABLE {table} ADD COLUMN reviewer_id INTEGER REFERENCES reviewers(reviewer_id)"
            )
    conn.commit()


def upsert_products(conn: sqlite3.Connection, products: list[dict]) -> None:
    """Insert or update products. Maps 'size' -> 'variant'."""
    sql = """
        INSERT INTO products (product_id, title, brand, model, variant,
                              pack_quantity, unit, image_ref, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(product_id) DO UPDATE SET
            title         = excluded.title,
            brand         = excluded.brand,
            model         = excluded.model,
            variant       = excluded.variant,
            pack_quantity = excluded.pack_quantity,
            unit          = excluded.unit,
            image_ref     = excluded.image_ref,
            raw_json      = excluded.raw_json
    """
    rows = []
    for p in products:
        variant = p.get("variant") if p.get("variant") is not None else p.get("size")
        image = p.get("image_ref") if p.get("image_ref") is not None else p.get("image_reference")
        rows.append((
            p["product_id"],
            p.get("title"),
            p.get("brand"),
            p.get("model"),
            variant,
            p.get("pack_quantity"),
            p.get("unit"),
            image,
            json.dumps(p),
        ))
    conn.executemany(sql, rows)
    conn.commit()


def load_labelled_pairs(conn: sqlite3.Connection, pairs: list[dict]) -> None:
    """Store ground-truth labelled pairs (upsert)."""
    sql = """
        INSERT INTO labelled_pairs (pair_key, is_duplicate)
        VALUES (?, ?)
        ON CONFLICT(pair_key) DO UPDATE SET is_duplicate = excluded.is_duplicate
    """
    rows = [(pair_key(p["a"], p["b"]), int(p["duplicate"])) for p in pairs]
    conn.executemany(sql, rows)
    conn.commit()


def save_suggestions(conn: sqlite3.Connection, suggestions: list[dict]) -> int:
    """Save new suggestions. Returns number of NEW rows inserted."""
    sql = """
        INSERT INTO suggestions (pair_key, id_a, id_b, confidence,
                                 reasons_json, flags_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(pair_key) DO NOTHING
    """
    before = conn.execute("SELECT COUNT(*) FROM suggestions").fetchone()[0]
    rows = []
    for s in suggestions:
        a, b = sorted([s["id_a"], s["id_b"]])
        rows.append((
            pair_key(a, b),
            a,
            b,
            s["confidence"],
            json.dumps(s["reasons"]),
            json.dumps(s.get("flags", [])),
            now(),
        ))
    conn.executemany(sql, rows)
    conn.commit()
    after = conn.execute("SELECT COUNT(*) FROM suggestions").fetchone()[0]
    return after - before


def get_decided_keys(conn: sqlite3.Connection) -> set[str]:
    """Return set of pair_keys that have a decision."""
    rows = conn.execute("SELECT pair_key FROM decisions").fetchall()
    return {r["pair_key"] for r in rows}


def get_pending(conn: sqlite3.Connection) -> list[dict]:
    """Suggestions with no decision, ordered by confidence DESC, with product details."""
    sql = """
        SELECT s.pair_key, s.id_a, s.id_b, s.confidence,
               s.reasons_json, s.flags_json, s.created_at,
               pa.product_id AS pa_id, pa.title AS pa_title, pa.brand AS pa_brand,
               pa.model AS pa_model, pa.variant AS pa_variant,
               pa.pack_quantity AS pa_pack_quantity, pa.unit AS pa_unit,
               pa.image_ref AS pa_image_ref, pa.raw_json AS pa_raw_json,
               pb.product_id AS pb_id, pb.title AS pb_title, pb.brand AS pb_brand,
               pb.model AS pb_model, pb.variant AS pb_variant,
               pb.pack_quantity AS pb_pack_quantity, pb.unit AS pb_unit,
               pb.image_ref AS pb_image_ref, pb.raw_json AS pb_raw_json
        FROM suggestions s
        JOIN products pa ON pa.product_id = s.id_a
        JOIN products pb ON pb.product_id = s.id_b
        LEFT JOIN decisions d ON d.pair_key = s.pair_key
        WHERE d.pair_key IS NULL
        ORDER BY s.confidence DESC
    """
    results = []
    for r in conn.execute(sql).fetchall():
        results.append({
            "pair_key": r["pair_key"],
            "id_a": r["id_a"],
            "id_b": r["id_b"],
            "confidence": r["confidence"],
            "reasons": json.loads(r["reasons_json"]),
            "flags": json.loads(r["flags_json"]),
            "created_at": r["created_at"],
            "product_a": {
                "product_id": r["pa_id"], "title": r["pa_title"],
                "brand": r["pa_brand"], "model": r["pa_model"],
                "variant": r["pa_variant"],
                "pack_quantity": r["pa_pack_quantity"],
                "unit": r["pa_unit"], "image_ref": r["pa_image_ref"],
                "raw_json": r["pa_raw_json"],
            },
            "product_b": {
                "product_id": r["pb_id"], "title": r["pb_title"],
                "brand": r["pb_brand"], "model": r["pb_model"],
                "variant": r["pb_variant"],
                "pack_quantity": r["pb_pack_quantity"],
                "unit": r["pb_unit"], "image_ref": r["pb_image_ref"],
                "raw_json": r["pb_raw_json"],
            },
        })
    return results


def get_suggestion(conn: sqlite3.Connection, key: str) -> dict | None:
    """Return a single suggestion row as dict, or None."""
    row = conn.execute(
        "SELECT * FROM suggestions WHERE pair_key = ?", (key,)
    ).fetchone()
    if row is None:
        return None
    return {
        "pair_key": row["pair_key"],
        "id_a": row["id_a"],
        "id_b": row["id_b"],
        "confidence": row["confidence"],
        "reasons": json.loads(row["reasons_json"]),
        "flags": json.loads(row["flags_json"]),
        "created_at": row["created_at"],
    }


def record_decision(
    conn: sqlite3.Connection,
    key: str,
    decision: str,
    reviewer: str,
    note: str | None = None,
    time_spent: float | None = None,
    reviewer_id: int | None = None,
) -> None:
    """Record or update a decision. Appends to decision_log every time."""
    if decision not in ("accept", "reject"):
        raise ValueError(f"Invalid decision: {decision!r}")
    if get_suggestion(conn, key) is None:
        raise KeyError(f"No suggestion for pair_key: {key!r}")

    if reviewer_id is not None:
        row = conn.execute(
            "SELECT username, is_active FROM reviewers WHERE reviewer_id = ?",
            (reviewer_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Unknown reviewer_id: {reviewer_id}")
        if row["is_active"] != 1:
            raise ValueError(f"Inactive reviewer_id: {reviewer_id}")
        reviewer = row["username"]

    ts = now()
    try:
        conn.execute(
            """
            INSERT INTO decisions (pair_key, decision, reviewer, note,
                                   time_spent_seconds, decided_at, reviewer_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(pair_key) DO UPDATE SET
                decision           = excluded.decision,
                reviewer           = excluded.reviewer,
                note               = excluded.note,
                time_spent_seconds = excluded.time_spent_seconds,
                decided_at         = excluded.decided_at,
                reviewer_id        = excluded.reviewer_id
            """,
            (key, decision, reviewer, note, time_spent, ts, reviewer_id),
        )
        conn.execute(
            """
            INSERT INTO decision_log (pair_key, decision, reviewer, decided_at, reviewer_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (key, decision, reviewer, ts, reviewer_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def get_setting(conn: sqlite3.Connection, key: str, default: str | None = None) -> str | None:
    """Read a setting value."""
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    """Write a setting value."""
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    conn.commit()
