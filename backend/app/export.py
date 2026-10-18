import csv
import io
import json

from app.db import get_decided_keys


def reviewed_rows(conn) -> list[dict]:
    """Return only pairs that have a decision, enriched with titles."""
    sql = """
        SELECT s.pair_key, s.id_a, s.id_b,
               pa.title AS title_a, pb.title AS title_b,
               s.confidence, s.reasons_json, s.flags_json,
               d.decision, d.reviewer, d.note,
               d.time_spent_seconds, d.decided_at
        FROM decisions d
        JOIN suggestions s ON s.pair_key = d.pair_key
        JOIN products pa ON pa.product_id = s.id_a
        JOIN products pb ON pb.product_id = s.id_b
        ORDER BY d.decided_at
    """
    results = []
    for r in conn.execute(sql).fetchall():
        results.append({
            "pair_key": r["pair_key"],
            "id_a": r["id_a"],
            "id_b": r["id_b"],
            "title_a": r["title_a"],
            "title_b": r["title_b"],
            "confidence": r["confidence"],
            "reasons": "; ".join(json.loads(r["reasons_json"])),
            "flags": "; ".join(json.loads(r["flags_json"])),
            "decision": r["decision"],
            "reviewer": r["reviewer"],
            "note": r["note"],
            "time_spent_seconds": r["time_spent_seconds"],
            "decided_at": r["decided_at"],
        })
    return results


_COLUMNS = [
    "pair_key", "id_a", "id_b", "title_a", "title_b",
    "confidence", "reasons", "flags", "decision", "reviewer",
    "note", "time_spent_seconds", "decided_at",
]


def export_json(conn) -> str:
    """Export reviewed pairs as JSON string."""
    return json.dumps(reviewed_rows(conn), indent=2)


def export_csv(conn) -> str:
    """Export reviewed pairs as CSV string. Always includes header."""
    rows = reviewed_rows(conn)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_COLUMNS)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


_PRODUCT_COLUMNS = [
    "product_id", "title", "brand", "model",
    "variant", "pack_quantity", "unit", "image_ref",
]


def export_products_csv(conn) -> str:
    """Export all products as CSV string. Always includes header."""
    sql = """
        SELECT product_id, title, brand, model, variant, pack_quantity, unit, image_ref
        FROM products
        ORDER BY product_id
    """
    rows = [dict(r) for r in conn.execute(sql).fetchall()]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_PRODUCT_COLUMNS)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def export_products_json(conn) -> str:
    """Export all products as JSON string."""
    sql = """
        SELECT product_id, title, brand, model, variant, pack_quantity, unit, image_ref
        FROM products
        ORDER BY product_id
    """
    rows = [dict(r) for r in conn.execute(sql).fetchall()]
    return json.dumps(rows, indent=2)
