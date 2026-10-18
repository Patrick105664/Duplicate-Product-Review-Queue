import sqlite3
from app.db import now


def save_metric_snapshot(
    conn: sqlite3.Connection,
    *,
    source: str,
    true_positives: int,
    false_positives: int,
    false_negatives: int,
    true_negatives: int,
    precision: float | None = None,
    recall: float | None = None,
    accuracy: float | None = None,
    precision_num: int | None = None,
    precision_den: int | None = None,
    recall_num: int | None = None,
    recall_den: int | None = None,
    accuracy_num: int | None = None,
    accuracy_den: int | None = None,
    threshold: float | None = None,
    label: str | None = None,
    notes: str | None = None,
) -> int:
    """Store evaluation metrics snapshot exactly as provided and return snapshot_id."""
    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be a non-empty string")

    for name, val in [
        ("true_positives", true_positives),
        ("false_positives", false_positives),
        ("false_negatives", false_negatives),
        ("true_negatives", true_negatives),
    ]:
        if not isinstance(val, int) or isinstance(val, bool) or val < 0:
            raise ValueError(f"{name} must be a non-negative integer")

    for name, val in [
        ("precision", precision),
        ("recall", recall),
        ("accuracy", accuracy),
    ]:
        if val is not None:
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                raise ValueError(f"{name} must be a number between 0 and 1")
            if val < 0.0 or val > 1.0:
                raise ValueError(f"{name} must be between 0 and 1, got {val}")

    num_den_checks = [
        ("precision", precision_num, precision_den, true_positives, true_positives + false_positives),
        ("recall", recall_num, recall_den, true_positives, true_positives + false_negatives),
        (
            "accuracy",
            accuracy_num,
            accuracy_den,
            true_positives + true_negatives,
            true_positives + false_positives + false_negatives + true_negatives,
        ),
    ]

    for name, num, den, exp_num, exp_den in num_den_checks:
        if num is not None or den is not None:
            if num is None or den is None:
                raise ValueError(f"Both {name}_num and {name}_den must be provided together")
            if (
                isinstance(num, bool)
                or not isinstance(num, int)
                or isinstance(den, bool)
                or not isinstance(den, int)
            ):
                raise ValueError(f"{name} numerator and denominator must be integers")
            if den <= 0:
                raise ValueError(f"{name} denominator must be greater than 0")
            if num < 0 or num > den:
                raise ValueError(f"{name} numerator must be >= 0 and <= denominator")
            if num != exp_num or den != exp_den:
                raise ValueError(
                    f"{name} fraction ({num}/{den}) does not match counts ({exp_num}/{exp_den})"
                )

    created_at = now()
    sql = """
        INSERT INTO metric_snapshots (
            label, source, threshold,
            true_positives, false_positives, false_negatives, true_negatives,
            precision, recall, accuracy,
            precision_num, precision_den,
            recall_num, recall_den,
            accuracy_num, accuracy_den,
            notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor = conn.execute(
        sql,
        (
            label,
            source.strip(),
            threshold,
            true_positives,
            false_positives,
            false_negatives,
            true_negatives,
            precision,
            recall,
            accuracy,
            precision_num,
            precision_den,
            recall_num,
            recall_den,
            accuracy_num,
            accuracy_den,
            notes,
            created_at,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def get_metric_snapshot(conn: sqlite3.Connection, snapshot_id: int) -> dict | None:
    """Retrieve a metric snapshot by snapshot_id."""
    row = conn.execute(
        "SELECT * FROM metric_snapshots WHERE snapshot_id = ?", (snapshot_id,)
    ).fetchone()
    if row is None:
        return None
    return dict(row)


def get_latest_metrics(conn: sqlite3.Connection) -> dict | None:
    """Retrieve the most recent metric snapshot by snapshot_id."""
    row = conn.execute(
        "SELECT * FROM metric_snapshots ORDER BY snapshot_id DESC LIMIT 1"
    ).fetchone()
    if row is None:
        return None
    return dict(row)


def list_metric_snapshots(conn: sqlite3.Connection, limit: int = 50) -> list[dict]:
    """List metric snapshots ordered newest first."""
    rows = conn.execute(
        "SELECT * FROM metric_snapshots ORDER BY snapshot_id DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(r) for r in rows]


def delete_metric_snapshot(conn: sqlite3.Connection, snapshot_id: int) -> None:
    """Delete a metric snapshot by snapshot_id, raising KeyError if unknown."""
    row = conn.execute(
        "SELECT 1 FROM metric_snapshots WHERE snapshot_id = ?", (snapshot_id,)
    ).fetchone()
    if row is None:
        raise KeyError(f"Snapshot not found: {snapshot_id}")
    conn.execute("DELETE FROM metric_snapshots WHERE snapshot_id = ?", (snapshot_id,))
    conn.commit()
