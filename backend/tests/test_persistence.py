import sqlite3
import pytest
from app.db import (
    pair_key, init_db, get_conn, upsert_products, save_suggestions,
    get_pending, record_decision, get_decided_keys, get_suggestion,
    get_setting, set_setting,
)


def test_pair_key_order_independent():
    assert pair_key("X02", "X01") == pair_key("X01", "X02") == "X01|X02"


def test_init_db_twice(conn):
    init_db(conn)
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    names = {r["name"] for r in rows}
    assert "products" in names
    assert "suggestions" in names


def test_rescan_inserts_zero_second_time(seeded_conn, sample_suggestions):
    new = save_suggestions(seeded_conn, sample_suggestions)
    assert new == 0
    count = seeded_conn.execute("SELECT COUNT(*) FROM suggestions").fetchone()[0]
    assert count == 2


def test_decided_pair_stays_decided_after_rescan(seeded_conn, sample_suggestions):
    key = pair_key("X01", "X02")
    record_decision(seeded_conn, key, "accept", "alice", time_spent=12.5)
    save_suggestions(seeded_conn, sample_suggestions)
    pending = get_pending(seeded_conn)
    pending_keys = [p["pair_key"] for p in pending]
    assert key not in pending_keys
    dec_count = seeded_conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
    assert dec_count == 1


def test_decision_survives_restart(db_path, sample_products, sample_suggestions):
    c1 = get_conn(db_path)
    init_db(c1)
    upsert_products(c1, sample_products)
    save_suggestions(c1, sample_suggestions)
    key = pair_key("X01", "X02")
    record_decision(c1, key, "accept", "bob")
    c1.close()

    c2 = get_conn(db_path)
    init_db(c2)
    assert key in get_decided_keys(c2)
    s = get_suggestion(c2, key)
    assert s is not None
    c2.close()


def test_rescan_does_not_overwrite_existing_suggestion(seeded_conn):
    key = pair_key("X01", "X02")
    original = get_suggestion(seeded_conn, key)
    new_suggestions = [
        {"id_a": "X01", "id_b": "X02", "confidence": 0.50,
         "reasons": ["changed"]},
    ]
    save_suggestions(seeded_conn, new_suggestions)
    after = get_suggestion(seeded_conn, key)
    assert after["confidence"] == original["confidence"]
    assert after["reasons"] == original["reasons"]


def test_unknown_pair_key_raises_key_error(seeded_conn):
    with pytest.raises(KeyError):
        record_decision(seeded_conn, "NOPE|NADA", "accept", "alice")


def test_invalid_decision_raises_value_error(seeded_conn):
    key = pair_key("X01", "X02")
    with pytest.raises(ValueError):
        record_decision(seeded_conn, key, "maybe", "alice")


def test_null_pack_quantity_stays_null(conn):
    prods = [
        {"product_id": "Z01", "brand": "Test", "model": "T",
         "pack_quantity": None, "size": "S", "title": "Null PQ"},
    ]
    upsert_products(conn, prods)
    row = conn.execute(
        "SELECT pack_quantity FROM products WHERE product_id = 'Z01'"
    ).fetchone()
    assert row["pack_quantity"] is None


def test_size_maps_to_variant(conn):
    prods = [
        {"product_id": "Z02", "brand": "Test", "model": "T",
         "size": "XL", "title": "Variant test"},
    ]
    upsert_products(conn, prods)
    row = conn.execute(
        "SELECT variant FROM products WHERE product_id = 'Z02'"
    ).fetchone()
    assert row["variant"] == "XL"


def test_changing_decision_appends_audit_log(seeded_conn):
    key = pair_key("X01", "X02")
    record_decision(seeded_conn, key, "accept", "alice")
    record_decision(seeded_conn, key, "reject", "bob")
    dec = seeded_conn.execute(
        "SELECT decision FROM decisions WHERE pair_key = ?", (key,)
    ).fetchone()
    assert dec["decision"] == "reject"
    logs = seeded_conn.execute(
        "SELECT * FROM decision_log WHERE pair_key = ?", (key,)
    ).fetchall()
    assert len(logs) == 2
    assert logs[0]["decision"] == "accept"
    assert logs[1]["decision"] == "reject"


def test_upsert_products_twice_no_duplicates(conn, sample_products):
    upsert_products(conn, sample_products)
    upsert_products(conn, sample_products)
    count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    assert count == len(sample_products)


def test_foreign_key_enforcement(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO suggestions
               (pair_key, id_a, id_b, confidence, reasons_json, flags_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("FAKE|PAIR", "FAKE", "PAIR", 0.5, "[]", "[]", "2024-01-01"),
        )


def test_settings_round_trip(conn):
    assert get_setting(conn, "threshold") is None
    assert get_setting(conn, "threshold", "0.7") == "0.7"
    set_setting(conn, "threshold", "0.85")
    assert get_setting(conn, "threshold") == "0.85"
    set_setting(conn, "threshold", "0.90")
    assert get_setting(conn, "threshold") == "0.90"


def test_end_to_end_fixture_flow(db_path):
    fixture = {
        "records": {
            "products": [
                {"product_id": f"X{i:02d}", "brand": "Demo",
                 "model": f"M{(i+1)//2}", "pack_quantity": 1 if i != 20 else 2,
                 "size": "M", "title": f"Sample {(i+1)//2}"}
                for i in range(1, 21)
            ],
            "labelled_pairs": [
                {"a": f"X{i:02d}", "b": f"X{i+1:02d}", "duplicate": True}
                for i in range(1, 19, 2)
            ] + [
                {"a": "X19", "b": "X20", "duplicate": False},
            ],
        }
    }

    from app.db import load_labelled_pairs
    from app.evaluation import false_merge_count

    c = get_conn(db_path)
    init_db(c)
    upsert_products(c, fixture["records"]["products"])
    load_labelled_pairs(c, fixture["records"]["labelled_pairs"])

    suggestions = [
        {"id_a": f"X{i:02d}", "id_b": f"X{i+1:02d}",
         "confidence": 0.9, "reasons": ["same model"]}
        for i in range(1, 19, 2)
    ]
    n1 = save_suggestions(c, suggestions)
    assert n1 == 9

    for s in suggestions:
        key = pair_key(s["id_a"], s["id_b"])
        record_decision(c, key, "accept", "tester", time_spent=5.0)

    assert false_merge_count(c) == 0

    n2 = save_suggestions(c, suggestions)
    assert n2 == 0
    assert len(get_pending(c)) == 0

    c.close()
