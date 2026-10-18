
import sqlite3

from app.db import (
    record_decision,
    get_suggestion,
    get_setting,
)
from app.export import (
    export_csv,
    export_json,
    export_products_csv,
    export_products_json,
)
from app.evaluation import (
    false_merge_count,
    avg_review_seconds,
    decision_counts,
)
from app.metrics_store import get_latest_metrics
from app.flags import flag_pair
from app.queries import (
    list_pairs,
    get_pair,
    list_products,
    get_product,
    accepted_since,
    count_products,
)
from app.scans import (
    list_scan_runs,
    get_scan_run,
    scans_this_month,
)


def ui_pair_id(pair_id: str) -> str:
    """Normalize pair IDs accepting '~' in place of '|'."""
    return pair_id.replace("~", "|")


def _to_ui_product(p: dict) -> dict:
    extra = p.get("extra") or {}
    status_val = extra.get("status")

    return {
        "id": p.get("product_id"),
        "title": p.get("title"),
        "brand": p.get("brand"),
        "model": p.get("model"),
        "category": extra.get("category"),
        "price": extra.get("price"),
        "sku": extra.get("sku"),
        "status": status_val if status_val is not None else "active",
        "image": p.get("image_ref"),
        "updatedAt": extra.get("updatedAt"),
        "variant": p.get("variant"),
        "pack_quantity": p.get("pack_quantity"),
        "unit": p.get("unit"),
    }


def _to_ui_pair(pair: dict) -> dict:
    conf = pair["confidence"]
    score = conf / 100.0 if conf > 1.0 else conf

    decision = pair.get("decision")

    if decision == "accept":
        status = "accepted"
    elif decision == "reject":
        status = "rejected"
    elif pair.get("flagged"):
        status = "flagged"
    else:
        status = "pending"

    search_text = " ".join(
        (pair.get("flags") or []) + (pair.get("reasons") or [])
    ).lower()

    label = (
        "Needs careful review"
        if "careful" in search_text or "missing brand" in search_text
        else None
    )

    return {
        "id": pair["pair_key"],
        "leftId": pair["id_a"],
        "rightId": pair["id_b"],
        "score": score,
        "status": status,
        "reason": "; ".join(pair.get("reasons") or []),
        "signals": pair.get("flags") or [],
        "createdAt": pair.get("created_at"),
        "label": label,
        "product_a": _to_ui_product(pair["product_a"]),
        "product_b": _to_ui_product(pair["product_b"]),
    }


def ui_pairs(
    conn: sqlite3.Connection,
    status: str | None = None,
) -> list[dict]:
    """Return suggestions mapped to the frontend pair format."""
    pairs = list_pairs(conn, status=status)
    return [_to_ui_pair(pair) for pair in pairs]


def ui_pair(
    conn: sqlite3.Connection,
    pair_id: str,
) -> dict | None:
    """Return one suggestion mapped to the frontend pair format."""
    pair = get_pair(conn, ui_pair_id(pair_id))

    if pair is None:
        return None

    return _to_ui_pair(pair)


def ui_products(conn: sqlite3.Connection) -> list[dict]:
    """Return all products mapped to the frontend product format."""
    return [_to_ui_product(product) for product in list_products(conn)]


def ui_product(
    conn: sqlite3.Connection,
    product_id: str,
) -> dict | None:
    """Return one product mapped to the frontend product format."""
    product = get_product(conn, product_id)

    if product is None:
        return None

    return _to_ui_product(product)


def submit_ui_decision(
    conn: sqlite3.Connection,
    pair_id: str,
    decision: str,
    note: str | None = None,
    reviewer: str = "Demo Reviewer",
    time_spent: float | None = None,
    reviewer_id: int | None = None,
) -> dict:
    """Record an accept, reject, or flag action from the frontend."""
    key = ui_pair_id(pair_id)

    if get_suggestion(conn, key) is None:
        raise KeyError(f"Unknown pair: {key!r}")

    if decision in ("accepted", "accept"):
        record_decision(
            conn,
            key,
            "accept",
            reviewer=reviewer,
            note=note,
            time_spent=time_spent,
            reviewer_id=reviewer_id,
        )
        echo = "accepted"

        row = conn.execute(
            "SELECT decided_at FROM decisions WHERE pair_key = ?",
            (key,),
        ).fetchone()
        decided_at = row["decided_at"]

    elif decision in ("rejected", "reject"):
        record_decision(
            conn,
            key,
            "reject",
            reviewer=reviewer,
            note=note,
            time_spent=time_spent,
            reviewer_id=reviewer_id,
        )
        echo = "rejected"

        row = conn.execute(
            "SELECT decided_at FROM decisions WHERE pair_key = ?",
            (key,),
        ).fetchone()
        decided_at = row["decided_at"]

    elif decision in ("flagged", "flag"):
        result = flag_pair(
            conn,
            key,
            reviewer=reviewer,
            note=note,
        )
        echo = "flagged"
        decided_at = result["flagged_at"]

    else:
        raise ValueError(f"Invalid decision: {decision!r}")

    return {
        "ok": True,
        "pairId": key,
        "decision": echo,
        "note": note,
        "decidedAt": decided_at,
    }


def ui_metrics(conn: sqlite3.Connection) -> dict:
    """Return evaluation and review metrics for the frontend."""
    counts = decision_counts(conn)
    total_products = count_products(conn)
    pending_reviews = len(ui_pairs(conn, status="pending"))
    accepted_week = accepted_since(conn, 7)

    scans_month = scans_this_month(conn)

    snapshot = get_latest_metrics(conn)

    if snapshot is not None:
        precision = (
            round(snapshot["precision"] * 100.0, 1)
            if snapshot["precision"] is not None
            else None
        )
        recall = (
            round(snapshot["recall"] * 100.0, 1)
            if snapshot["recall"] is not None
            else None
        )

        precision_correct = snapshot["precision_num"]
        precision_reviewed = snapshot["precision_den"]
        recall_found = snapshot["recall_num"]
        recall_expected = snapshot["recall_den"]
    else:
        precision = None
        recall = None
        precision_correct = None
        precision_reviewed = None
        recall_found = None
        recall_expected = None

    average_info = avg_review_seconds(conn)
    average_seconds = (
        average_info["avg_seconds"]
        if average_info["n"] > 0
        else None
    )

    accepted_count = counts["accept"]
    false_merges = false_merge_count(conn)

    false_merge_rate = (
        false_merges / accepted_count * 100.0
        if accepted_count > 0
        else None
    )

    cost_value = get_setting(conn, "false_merge_cost_inr")

    try:
        false_merge_cost_inr = (
            int(cost_value) if cost_value is not None else None
        )
    except (ValueError, TypeError):
        false_merge_cost_inr = None

    return {
        "totalProducts": total_products,
        "pendingReviews": pending_reviews,
        "acceptedThisWeek": accepted_week,
        "scansThisMonth": scans_month,
        "precision": precision,
        "precisionCorrect": precision_correct,
        "precisionReviewed": precision_reviewed,
        "recall": recall,
        "recallFound": recall_found,
        "recallExpected": recall_expected,
        "avgReviewTimeSeconds": average_seconds,
        "falseMergeRate": false_merge_rate,
        "note": "Synthetic fixture. Not evidence of production performance.",
        "falseMergeCount": false_merges,
        "falseMergeCostInr": false_merge_cost_inr,
        "falseMergeCostNote": "Assumption, not observed data",
    }


def ui_scans(
    conn: sqlite3.Connection,
    limit: int = 50,
) -> list[dict]:
    """Return scan history formatted for the frontend."""
    runs = list_scan_runs(conn, limit=limit)

    return [
        {
            "id": f"SCAN-{run['scan_id']:04d}",
            "startedAt": run["started_at"],
            "source": run["source"],
            "products": run["products_count"],
            "pairs": run["pairs_found"],
            "status": run["status"],
            "duration": run["duration_seconds"],
        }
        for run in runs
    ]


def ui_rescan_result(
    conn: sqlite3.Connection,
    scan_id: int,
) -> dict:
    """Return the result of a completed scan."""
    run = get_scan_run(conn, scan_id)

    if run is None:
        raise KeyError(f"Unknown scan_id: {scan_id}")

    new_pairs = run["new_pairs"] if run["new_pairs"] is not None else 0

    return {
        "id": f"SCAN-{scan_id:04d}",
        "status": run["status"],
        "message": f"Scan completed: {new_pairs} new pairs",
    }


def ui_export(
    conn: sqlite3.Connection,
    fmt: str,
    kind: str,
) -> tuple[str, str, str]:
    """Return (content, media type, filename) for export requests."""
    if kind not in ("reviews", "products"):
        raise ValueError(f"Invalid export kind: {kind!r}")

    if fmt not in ("csv", "json"):
        raise ValueError(f"Invalid export format: {fmt!r}")

    if kind == "reviews":
        if fmt == "csv":
            return (
                export_csv(conn),
                "text/csv; charset=utf-8",
                "reviews.csv",
            )

        return (
            export_json(conn),
            "application/json",
            "reviews.json",
        )

    if fmt == "csv":
        return (
            export_products_csv(conn),
            "text/csv; charset=utf-8",
            "products.csv",
        )

    return (
        export_products_json(conn),
        "application/json",
        "products.json",
    )
