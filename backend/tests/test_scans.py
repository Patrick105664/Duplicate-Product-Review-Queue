from datetime import datetime, timezone
import pytest

from app.db import get_conn, init_db
from app.scans import (
    start_scan_run,
    finish_scan_run,
    list_scan_runs,
    get_scan_run,
    scans_this_month,
)


def test_scan_lifecycle_and_duration(conn):
    sid = start_scan_run(conn, source="test-source")
    assert isinstance(sid, int)

    run_start = get_scan_run(conn, sid)
    assert run_start["status"] == "running"
    assert run_start["finished_at"] is None
    assert run_start["duration_seconds"] is None

    finish_scan_run(
        conn,
        sid,
        products_count=20,
        pairs_found=14,
        new_pairs=10,
        status="completed",
    )

    run_fin = get_scan_run(conn, sid)
    assert run_fin["status"] == "completed"
    assert run_fin["products_count"] == 20
    assert run_fin["pairs_found"] == 14
    assert run_fin["new_pairs"] == 10
    assert run_fin["finished_at"] is not None
    assert run_fin["duration_seconds"] is not None
    assert run_fin["duration_seconds"] >= 0.0


def test_scan_failed_status_and_validations(conn):
    sid = start_scan_run(conn)

    with pytest.raises(ValueError):
        finish_scan_run(
            conn,
            sid,
            products_count=0,
            pairs_found=0,
            new_pairs=0,
            status="invalid_status",
        )

    with pytest.raises(KeyError):
        finish_scan_run(
            conn,
            999999,
            products_count=0,
            pairs_found=0,
            new_pairs=0,
            status="completed",
        )

    finish_scan_run(
        conn,
        sid,
        products_count=5,
        pairs_found=0,
        new_pairs=0,
        status="failed",
        error="Matcher error",
    )
    run = get_scan_run(conn, sid)
    assert run["status"] == "failed"
    assert run["error"] == "Matcher error"


def test_list_scans_newest_first(conn):
    sid1 = start_scan_run(conn, "source-1")
    sid2 = start_scan_run(conn, "source-2")
    sid3 = start_scan_run(conn, "source-3")

    runs = list_scan_runs(conn, limit=2)
    assert len(runs) == 2
    assert [r["scan_id"] for r in runs] == [sid3, sid2]


def test_scans_this_month_and_backdating(conn):
    start_scan_run(conn)
    assert scans_this_month(conn) == 1

    prior_date = "2020-01-01T00:00:00+00:00"
    conn.execute(
        "INSERT INTO scan_runs (started_at, source, status) VALUES (?, 'old', 'completed')",
        (prior_date,),
    )
    conn.commit()

    assert scans_this_month(conn) == 1


def test_scan_survives_restart(db_path):
    conn1 = get_conn(db_path)
    init_db(conn1)
    sid = start_scan_run(conn1, "persist-test")
    finish_scan_run(
        conn1,
        sid,
        products_count=100,
        pairs_found=5,
        new_pairs=2,
        status="completed",
    )
    conn1.close()

    conn2 = get_conn(db_path)
    run = get_scan_run(conn2, sid)
    assert run is not None
    assert run["source"] == "persist-test"
    assert run["products_count"] == 100
    conn2.close()
