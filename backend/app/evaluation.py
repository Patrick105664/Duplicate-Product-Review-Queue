def false_merge_count(conn) -> int:
    """Accepted pairs whose ground-truth label is NOT duplicate."""
    row = conn.execute("""
        SELECT COUNT(*) AS cnt
        FROM decisions d
        JOIN labelled_pairs lp ON lp.pair_key = d.pair_key
        WHERE d.decision = 'accept' AND lp.is_duplicate = 0
    """).fetchone()
    return row["cnt"]


def avg_review_seconds(conn) -> dict:
    """Average review time, ignoring NULLs."""
    row = conn.execute("""
        SELECT AVG(time_spent_seconds) AS avg_s,
               COUNT(time_spent_seconds) AS n
        FROM decisions
        WHERE time_spent_seconds IS NOT NULL
    """).fetchone()
    return {
        "avg_seconds": row["avg_s"],
        "n": row["n"],
    }


def decision_counts(conn) -> dict:
    """Counts of accept, reject, and pending suggestions."""
    total = conn.execute("SELECT COUNT(*) AS c FROM suggestions").fetchone()["c"]
    accepted = conn.execute(
        "SELECT COUNT(*) AS c FROM decisions WHERE decision = 'accept'"
    ).fetchone()["c"]
    rejected = conn.execute(
        "SELECT COUNT(*) AS c FROM decisions WHERE decision = 'reject'"
    ).fetchone()["c"]
    return {
        "accept": accepted,
        "reject": rejected,
        "pending": total - accepted - rejected,
    }


def reviewer_stats(conn) -> list[dict]:
    """Per-reviewer decision stats including unattributed decisions."""
    sql = """
        SELECT
            d.reviewer_id,
            r.username,
            r.display_name,
            SUM(CASE WHEN d.decision = 'accept' THEN 1 ELSE 0 END) AS accepts,
            SUM(CASE WHEN d.decision = 'reject' THEN 1 ELSE 0 END) AS rejects,
            COUNT(*) AS total,
            AVG(d.time_spent_seconds) AS avg_seconds
        FROM decisions d
        LEFT JOIN reviewers r ON r.reviewer_id = d.reviewer_id
        GROUP BY d.reviewer_id
        ORDER BY total DESC, username ASC
    """
    results = []
    for r in conn.execute(sql).fetchall():
        results.append({
            "username": r["username"] if r["username"] is not None else "(unattributed)",
            "display_name": r["display_name"],
            "accepts": r["accepts"],
            "rejects": r["rejects"],
            "avg_seconds": float(r["avg_seconds"]) if r["avg_seconds"] is not None else None,
            "total": r["total"],
        })
    return results
