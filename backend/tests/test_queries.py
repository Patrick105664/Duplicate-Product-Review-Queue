from datetime import datetime, timedelta, timezone
import pytest

from app.db import record_decision, upsert_products, save_suggestions
from app.flags import flag_pair
from app.queries import (
    list_pairs,
    get_pair,
    list_products,
    get_product,
    accepted_since,
    count_products,
)


def test_list_pairs_pending_and_decided_with_embedded_products(seeded_conn):
    record_decision(seeded_conn, "X01|X02", "accept", "alice")
    all_pairs = list_pairs(seeded_conn)
    assert len(all_pairs) == 2

    keys = {p["pair_key"] for p in all_pairs}
    assert keys == {"X01|X02", "X03|X04"}

    p_decided = [p for p in all_pairs if p["pair_key"] == "X01|X02"][0]
    assert p_decided["decision"] == "accept"
    assert p_decided["decided_at"] is not None
    assert p_decided["flagged"] is False
    assert p_decided["product_a"]["product_id"] == "X01"
    assert "raw_json" not in p_decided["product_a"]

    p_pending = [p for p in all_pairs if p["pair_key"] == "X03|X04"][0]
    assert p_pending["decision"] is None
    assert p_pending["decided_at"] is None
    assert p_pending["flagged"] is False


def test_status_filters_and_invalid_status_raises(seeded_conn):
    record_decision(seeded_conn, "X01|X02", "accept", "alice")
    flag_pair(seeded_conn, "X03|X04", "bob", note="Needs check")

    upsert_products(
        seeded_conn,
        [
            {"product_id": "X05", "title": "P5", "raw_json": "{}"},
            {"product_id": "X06", "title": "P6", "raw_json": "{}"},
            {"product_id": "X07", "title": "P7", "raw_json": "{}"},
            {"product_id": "X08", "title": "P8", "raw_json": "{}"},
        ],
    )
    save_suggestions(
        seeded_conn,
        [
            {"id_a": "X05", "id_b": "X06", "confidence": 0.8, "reasons": []},
            {"id_a": "X07", "id_b": "X08", "confidence": 0.7, "reasons": []},
        ],
    )
    record_decision(seeded_conn, "X05|X06", "reject", "alice")

    pending_list = list_pairs(seeded_conn, status="pending")
    assert len(pending_list) == 1
    assert pending_list[0]["pair_key"] == "X07|X08"

    flagged_list = list_pairs(seeded_conn, status="flagged")
    assert len(flagged_list) == 1
    assert flagged_list[0]["pair_key"] == "X03|X04"
    assert flagged_list[0]["flag_note"] == "Needs check"

    accepted_list = list_pairs(seeded_conn, status="accepted")
    assert len(accepted_list) == 1
    assert accepted_list[0]["pair_key"] == "X01|X02"

    rejected_list = list_pairs(seeded_conn, status="rejected")
    assert len(rejected_list) == 1
    assert rejected_list[0]["pair_key"] == "X05|X06"

    with pytest.raises(ValueError):
        list_pairs(seeded_conn, status="unknown_status")


def test_get_pair_details_and_unknown(seeded_conn):
    p = get_pair(seeded_conn, "X01|X02")
    assert p is not None
    assert p["pair_key"] == "X01|X02"
    assert p["id_a"] == "X01"
    assert p["id_b"] == "X02"

    assert get_pair(seeded_conn, "NONEXISTENT|PAIR") is None


def test_list_products_and_get_product(seeded_conn):
    prods = list_products(seeded_conn)
    assert len(prods) == 4
    assert count_products(seeded_conn) == 4

    p3 = get_product(seeded_conn, "X03")
    assert p3 is not None
    assert p3["product_id"] == "X03"
    assert p3["pack_quantity"] is None
    assert isinstance(p3["extra"], dict)

    assert get_product(seeded_conn, "UNKNOWN") is None


def test_accepted_since_filters_by_date(seeded_conn):
    record_decision(seeded_conn, "X01|X02", "accept", "alice")
    record_decision(seeded_conn, "X03|X04", "accept", "alice")

    assert accepted_since(seeded_conn, 7) == 2

    old_date = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    seeded_conn.execute(
        "UPDATE decisions SET decided_at = ? WHERE pair_key = 'X01|X02'",
        (old_date,),
    )
    seeded_conn.commit()

    assert accepted_since(seeded_conn, 7) == 1
    assert accepted_since(seeded_conn, 14) == 2
