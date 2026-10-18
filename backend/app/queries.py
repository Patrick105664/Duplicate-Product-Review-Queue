from datetime import datetime, timedelta, timezone
import json
import sqlite3


def list_pairs(conn: sqlite3.Connection, status: str | None = None) -> list[dict]:
    """List all suggestions with decisions, flags, and product details."""
    valid_statuses = (None, "pending", "accepted", "rejected", "flagged")
    if status not in valid_statuses:
        raise ValueError(f"Invalid status: {status!r}")

    sql = """
        SELECT
            s.pair_key, s.id_a, s.id_b, s.confidence,
            s.reasons_json, s.flags_json, s.created_at,
            d.decision, d.decided_at,
            pa.product_id AS pa_id, pa.title AS pa_title, pa.brand AS pa_brand,
            pa.model AS pa_model, pa.variant AS pa_variant,
            pa.pack_quantity AS pa_pack_quantity, pa.unit AS pa_unit,
            pa.image_ref AS pa_image_ref,
            pb.product_id AS pb_id, pb.title AS pb_title, pb.brand AS pb_brand,
            pb.model AS pb_model, pb.variant AS pb_variant,
            pb.pack_quantity AS pb_pack_quantity, pb.unit AS pb_unit,
            pb.image_ref AS pb_image_ref,
            flg.flag_id, flg.note AS flag_note
        FROM suggestions s
        JOIN products pa ON pa.product_id = s.id_a
        JOIN products pb ON pb.product_id = s.id_b
        LEFT JOIN decisions d ON d.pair_key = s.pair_key
        LEFT JOIN (
            SELECT pf.pair_key, pf.flag_id, pf.note
            FROM pair_flags pf
            WHERE pf.flag_id = (
                SELECT MAX(pf2.flag_id)
                FROM pair_flags pf2
                WHERE pf2.pair_key = pf.pair_key
            )
        ) flg ON flg.pair_key = s.pair_key
        ORDER BY s.created_at DESC
    """
    rows = conn.execute(sql).fetchall()
    results = []
    for r in rows:
        decision = r["decision"]
        has_flag = r["flag_id"] is not None
        flagged = bool(has_flag and decision is None)
        flag_note = r["flag_note"] if flagged else None

        if status == "pending" and (decision is not None or flagged):
            continue
        if status == "flagged" and not flagged:
            continue
        if status == "accepted" and decision != "accept":
            continue
        if status == "rejected" and decision != "reject":
            continue

        results.append({
            "pair_key": r["pair_key"],
            "id_a": r["id_a"],
            "id_b": r["id_b"],
            "confidence": r["confidence"],
            "reasons": json.loads(r["reasons_json"]),
            "flags": json.loads(r["flags_json"]),
            "created_at": r["created_at"],
            "product_a": {
                "product_id": r["pa_id"],
                "title": r["pa_title"],
                "brand": r["pa_brand"],
                "model": r["pa_model"],
                "variant": r["pa_variant"],
                "pack_quantity": r["pa_pack_quantity"],
                "unit": r["pa_unit"],
                "image_ref": r["pa_image_ref"],
            },
            "product_b": {
                "product_id": r["pb_id"],
                "title": r["pb_title"],
                "brand": r["pb_brand"],
                "model": r["pb_model"],
                "variant": r["pb_variant"],
                "pack_quantity": r["pb_pack_quantity"],
                "unit": r["pb_unit"],
                "image_ref": r["pb_image_ref"],
            },
            "decision": decision,
            "decided_at": r["decided_at"],
            "flagged": flagged,
            "flag_note": flag_note,
        })
    return results


def get_pair(conn: sqlite3.Connection, key: str) -> dict | None:
    """Return suggestion details for one pair_key, or None."""
    sql = """
        SELECT
            s.pair_key, s.id_a, s.id_b, s.confidence,
            s.reasons_json, s.flags_json, s.created_at,
            d.decision, d.decided_at,
            pa.product_id AS pa_id, pa.title AS pa_title, pa.brand AS pa_brand,
            pa.model AS pa_model, pa.variant AS pa_variant,
            pa.pack_quantity AS pa_pack_quantity, pa.unit AS pa_unit,
            pa.image_ref AS pa_image_ref,
            pb.product_id AS pb_id, pb.title AS pb_title, pb.brand AS pb_brand,
            pb.model AS pb_model, pb.variant AS pb_variant,
            pb.pack_quantity AS pb_pack_quantity, pb.unit AS pb_unit,
            pb.image_ref AS pb_image_ref,
            flg.flag_id, flg.note AS flag_note
        FROM suggestions s
        JOIN products pa ON pa.product_id = s.id_a
        JOIN products pb ON pb.product_id = s.id_b
        LEFT JOIN decisions d ON d.pair_key = s.pair_key
        LEFT JOIN (
            SELECT pf.pair_key, pf.flag_id, pf.note
            FROM pair_flags pf
            WHERE pf.flag_id = (
                SELECT MAX(pf2.flag_id)
                FROM pair_flags pf2
                WHERE pf2.pair_key = pf.pair_key
            )
        ) flg ON flg.pair_key = s.pair_key
        WHERE s.pair_key = ?
    """
    r = conn.execute(sql, (key,)).fetchone()
    if r is None:
        return None

    decision = r["decision"]
    has_flag = r["flag_id"] is not None
    flagged = bool(has_flag and decision is None)
    flag_note = r["flag_note"] if flagged else None

    return {
        "pair_key": r["pair_key"],
        "id_a": r["id_a"],
        "id_b": r["id_b"],
        "confidence": r["confidence"],
        "reasons": json.loads(r["reasons_json"]),
        "flags": json.loads(r["flags_json"]),
        "created_at": r["created_at"],
        "product_a": {
            "product_id": r["pa_id"],
            "title": r["pa_title"],
            "brand": r["pa_brand"],
            "model": r["pa_model"],
            "variant": r["pa_variant"],
            "pack_quantity": r["pa_pack_quantity"],
            "unit": r["pa_unit"],
            "image_ref": r["pa_image_ref"],
        },
        "product_b": {
            "product_id": r["pb_id"],
            "title": r["pb_title"],
            "brand": r["pb_brand"],
            "model": r["pb_model"],
            "variant": r["pb_variant"],
            "pack_quantity": r["pb_pack_quantity"],
            "unit": r["pb_unit"],
            "image_ref": r["pb_image_ref"],
        },
        "decision": decision,
        "decided_at": r["decided_at"],
        "flagged": flagged,
        "flag_note": flag_note,
    }


def list_products(conn: sqlite3.Connection) -> list[dict]:
    """List all products with parsed extra raw_json attributes."""
    sql = """
        SELECT product_id, title, brand, model, variant,
               pack_quantity, unit, image_ref, raw_json
        FROM products
        ORDER BY product_id ASC
    """
    rows = conn.execute(sql).fetchall()
    results = []
    for r in rows:
        raw = r["raw_json"]
        extra = json.loads(raw) if raw else {}
        results.append({
            "product_id": r["product_id"],
            "title": r["title"],
            "brand": r["brand"],
            "model": r["model"],
            "variant": r["variant"],
            "pack_quantity": r["pack_quantity"],
            "unit": r["unit"],
            "image_ref": r["image_ref"],
            "extra": extra,
        })
    return results


def get_product(conn: sqlite3.Connection, product_id: str) -> dict | None:
    """Get single product with parsed extra raw_json attributes."""
    sql = """
        SELECT product_id, title, brand, model, variant,
               pack_quantity, unit, image_ref, raw_json
        FROM products
        WHERE product_id = ?
    """
    r = conn.execute(sql, (product_id,)).fetchone()
    if r is None:
        return None
    raw = r["raw_json"]
    extra = json.loads(raw) if raw else {}
    return {
        "product_id": r["product_id"],
        "title": r["title"],
        "brand": r["brand"],
        "model": r["model"],
        "variant": r["variant"],
        "pack_quantity": r["pack_quantity"],
        "unit": r["unit"],
        "image_ref": r["image_ref"],
        "extra": extra,
    }


def accepted_since(conn: sqlite3.Connection, days: int) -> int:
    """Count of decisions accepted within the given number of days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    row = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM decisions
        WHERE decision = 'accept' AND decided_at >= ?
        """,
        (cutoff,),
    ).fetchone()
    return row["c"]


def count_products(conn: sqlite3.Connection) -> int:
    """Return total count of catalogue products."""
    row = conn.execute("SELECT COUNT(*) AS c FROM products").fetchone()
    return row["c"]
