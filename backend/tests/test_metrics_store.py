import sqlite3
import pytest

from app.db import get_conn, init_db
from app.metrics_store import (
    save_metric_snapshot,
    get_metric_snapshot,
    get_latest_metrics,
    list_metric_snapshots,
    delete_metric_snapshot,
)


def test_save_and_read_fixture_numbers(conn):
    sid = save_metric_snapshot(
        conn,
        source="fixture-eval",
        true_positives=9,
        false_positives=0,
        false_negatives=0,
        true_negatives=1,
        precision=1.0,
        recall=1.0,
        accuracy=1.0,
        precision_num=9,
        precision_den=9,
        recall_num=9,
        recall_den=9,
        accuracy_num=10,
        accuracy_den=10,
        threshold=0.75,
        label="initial baseline",
        notes="sample note",
    )
    assert isinstance(sid, int)
    snapshot = get_metric_snapshot(conn, sid)
    assert snapshot is not None
    assert snapshot["snapshot_id"] == sid
    assert snapshot["source"] == "fixture-eval"
    assert snapshot["true_positives"] == 9
    assert snapshot["false_positives"] == 0
    assert snapshot["false_negatives"] == 0
    assert snapshot["true_negatives"] == 1
    assert snapshot["precision"] == 1.0
    assert snapshot["recall"] == 1.0
    assert snapshot["accuracy"] == 1.0
    assert snapshot["precision_num"] == 9
    assert snapshot["precision_den"] == 9
    assert snapshot["recall_num"] == 9
    assert snapshot["recall_den"] == 9
    assert snapshot["accuracy_num"] == 10
    assert snapshot["accuracy_den"] == 10
    assert snapshot["threshold"] == 0.75
    assert snapshot["label"] == "initial baseline"
    assert snapshot["notes"] == "sample note"
    assert "created_at" in snapshot


def test_ratios_stored_as_given_and_not_recomputed(conn):
    # Pass precision=0.5 where counts are TP=5, FP=5 (or no num/den checks)
    sid = save_metric_snapshot(
        conn,
        source="matcher-eval",
        true_positives=1,
        false_positives=1,
        false_negatives=0,
        true_negatives=0,
        precision=0.5,
    )
    snapshot = get_metric_snapshot(conn, sid)
    assert snapshot["precision"] == 0.5
    # Recall and accuracy were not supplied, should be None, NOT computed
    assert snapshot["recall"] is None
    assert snapshot["accuracy"] is None


def test_null_ratios_stay_null_never_zero(conn):
    sid = save_metric_snapshot(
        conn,
        source="empty-eval",
        true_positives=0,
        false_positives=0,
        false_negatives=0,
        true_negatives=0,
        precision=None,
        recall=None,
        accuracy=None,
    )
    snapshot = get_metric_snapshot(conn, sid)
    assert snapshot["precision"] is None
    assert snapshot["recall"] is None
    assert snapshot["accuracy"] is None
    assert snapshot["precision"] != 0
    assert snapshot["recall"] != 0
    assert snapshot["accuracy"] != 0


def test_validation_errors_counts_ratios_and_source(conn):
    # Empty source
    with pytest.raises(ValueError):
        save_metric_snapshot(
            conn,
            source="   ",
            true_positives=1,
            false_positives=0,
            false_negatives=0,
            true_negatives=0,
        )

    # Negative counts
    with pytest.raises(ValueError):
        save_metric_snapshot(
            conn,
            source="eval",
            true_positives=-1,
            false_positives=0,
            false_negatives=0,
            true_negatives=0,
        )

    # Ratio > 1.0
    with pytest.raises(ValueError):
        save_metric_snapshot(
            conn,
            source="eval",
            true_positives=1,
            false_positives=0,
            false_negatives=0,
            true_negatives=0,
            precision=1.5,
        )

    # Ratio < 0.0
    with pytest.raises(ValueError):
        save_metric_snapshot(
            conn,
            source="eval",
            true_positives=1,
            false_positives=0,
            false_negatives=0,
            true_negatives=0,
            recall=-0.1,
        )


def test_num_den_disagreement_and_numerator_exceeding_denominator(conn):
    # num > den
    with pytest.raises(ValueError):
        save_metric_snapshot(
            conn,
            source="eval",
            true_positives=5,
            false_positives=0,
            false_negatives=0,
            true_negatives=0,
            precision_num=6,
            precision_den=5,
        )

    # num/den disagrees with counts: precision_num != TP or precision_den != TP + FP
    with pytest.raises(ValueError):
        save_metric_snapshot(
            conn,
            source="eval",
            true_positives=5,
            false_positives=5,
            false_negatives=0,
            true_negatives=0,
            precision_num=5,
            precision_den=9,  # Should be 10
        )

    # recall_den disagreement
    with pytest.raises(ValueError):
        save_metric_snapshot(
            conn,
            source="eval",
            true_positives=4,
            false_positives=1,
            false_negatives=2,
            true_negatives=1,
            recall_num=4,
            recall_den=7,  # Should be 4 + 2 = 6
        )

    # accuracy_num disagreement
    with pytest.raises(ValueError):
        save_metric_snapshot(
            conn,
            source="eval",
            true_positives=4,
            false_positives=1,
            false_negatives=2,
            true_negatives=3,
            accuracy_num=8,  # Should be 4 + 3 = 7
            accuracy_den=10,
        )


def test_get_latest_metrics_and_list_snapshots_order_and_limit(conn):
    sid1 = save_metric_snapshot(
        conn,
        source="eval-1",
        true_positives=1,
        false_positives=0,
        false_negatives=0,
        true_negatives=1,
        label="run 1",
    )
    sid2 = save_metric_snapshot(
        conn,
        source="eval-2",
        true_positives=2,
        false_positives=0,
        false_negatives=0,
        true_negatives=1,
        label="run 2",
    )
    sid3 = save_metric_snapshot(
        conn,
        source="eval-3",
        true_positives=3,
        false_positives=0,
        false_negatives=0,
        true_negatives=1,
        label="run 3",
    )

    latest = get_latest_metrics(conn)
    assert latest is not None
    assert latest["snapshot_id"] == sid3
    assert latest["label"] == "run 3"

    all_snaps = list_metric_snapshots(conn, limit=50)
    assert len(all_snaps) == 3
    assert [s["snapshot_id"] for s in all_snaps] == [sid3, sid2, sid1]

    limited = list_metric_snapshots(conn, limit=2)
    assert len(limited) == 2
    assert [s["snapshot_id"] for s in limited] == [sid3, sid2]


def test_unknown_snapshot_and_delete(conn):
    assert get_metric_snapshot(conn, 999999) is None

    sid = save_metric_snapshot(
        conn,
        source="eval",
        true_positives=1,
        false_positives=0,
        false_negatives=0,
        true_negatives=0,
    )
    delete_metric_snapshot(conn, sid)
    assert get_metric_snapshot(conn, sid) is None

    with pytest.raises(KeyError):
        delete_metric_snapshot(conn, 999999)


def test_snapshot_survives_restart(db_path):
    conn1 = get_conn(db_path)
    init_db(conn1)
    sid = save_metric_snapshot(
        conn1,
        source="eval-restart",
        true_positives=7,
        false_positives=1,
        false_negatives=2,
        true_negatives=4,
        precision=0.875,
        threshold=0.8,
        label="persistent snapshot",
    )
    conn1.close()

    conn2 = get_conn(db_path)
    snapshot = get_metric_snapshot(conn2, sid)
    assert snapshot is not None
    assert snapshot["source"] == "eval-restart"
    assert snapshot["true_positives"] == 7
    assert snapshot["precision"] == 0.875
    assert snapshot["label"] == "persistent snapshot"
    conn2.close()


def test_init_db_safe_twice_and_migrates_old_database(tmp_path):
    old_db = str(tmp_path / "old_metrics.db")
    conn = sqlite3.connect(old_db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript("""
        CREATE TABLE products (
            product_id TEXT PRIMARY KEY, title TEXT, brand TEXT, model TEXT,
            variant TEXT, pack_quantity INTEGER, unit TEXT, image_ref TEXT, raw_json TEXT NOT NULL
        );
        INSERT INTO products VALUES ('P1', 'title', 'brand', 'model', 'v', 1, 'u', 'img', '{}');
    """)
    conn.commit()

    # init_db creates metric_snapshots
    init_db(conn)
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert "metric_snapshots" in tables

    # Old row is preserved
    row = conn.execute("SELECT * FROM products WHERE product_id = 'P1'").fetchone()
    assert row["product_id"] == "P1"

    # Calling init_db again is safe and preserves data
    init_db(conn)
    row2 = conn.execute("SELECT * FROM products WHERE product_id = 'P1'").fetchone()
    assert row2["product_id"] == "P1"
    conn.close()
