from app.db import (
    pair_key, record_decision, load_labelled_pairs, upsert_products,
    save_suggestions,
)
from app.evaluation import false_merge_count, avg_review_seconds, decision_counts


def test_false_merge_zero_for_true_duplicates(seeded_conn):
    load_labelled_pairs(seeded_conn, [
        {"a": "X01", "b": "X02", "duplicate": True},
    ])
    record_decision(seeded_conn, pair_key("X01", "X02"), "accept", "alice")
    assert false_merge_count(seeded_conn) == 0


def test_false_merge_one_for_non_duplicate(seeded_conn):
    load_labelled_pairs(seeded_conn, [
        {"a": "X03", "b": "X04", "duplicate": False},
    ])
    record_decision(seeded_conn, pair_key("X03", "X04"), "accept", "alice")
    assert false_merge_count(seeded_conn) == 1


def test_reject_non_duplicate_not_false_merge(seeded_conn):
    load_labelled_pairs(seeded_conn, [
        {"a": "X03", "b": "X04", "duplicate": False},
    ])
    record_decision(seeded_conn, pair_key("X03", "X04"), "reject", "alice")
    assert false_merge_count(seeded_conn) == 0


def test_avg_review_seconds_ignores_nulls(seeded_conn):
    record_decision(seeded_conn, pair_key("X01", "X02"), "accept", "a", time_spent=10.0)
    record_decision(seeded_conn, pair_key("X03", "X04"), "reject", "b", time_spent=None)
    result = avg_review_seconds(seeded_conn)
    assert result["avg_seconds"] == 10.0
    assert result["n"] == 1


def test_avg_review_seconds_none_when_no_data(conn):
    result = avg_review_seconds(conn)
    assert result["avg_seconds"] is None
    assert result["n"] == 0


def test_decision_counts(seeded_conn):
    counts = decision_counts(seeded_conn)
    assert counts == {"accept": 0, "reject": 0, "pending": 2}

    record_decision(seeded_conn, pair_key("X01", "X02"), "accept", "a")
    counts = decision_counts(seeded_conn)
    assert counts == {"accept": 1, "reject": 0, "pending": 1}

    record_decision(seeded_conn, pair_key("X03", "X04"), "reject", "b")
    counts = decision_counts(seeded_conn)
    assert counts == {"accept": 1, "reject": 1, "pending": 0}
