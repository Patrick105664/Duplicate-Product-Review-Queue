import json
import pytest

from app.db import (
    get_conn,
    init_db,
    upsert_products,
    save_suggestions,
    load_labelled_pairs,
    set_setting,
)
from app.metrics_store import save_metric_snapshot
from app.scans import start_scan_run, finish_scan_run
from app.ui_adapter import (
    ui_pair_id,
    ui_pairs,
    ui_pair,
    ui_products,
    ui_product,
    submit_ui_decision,
    ui_metrics,
    ui_scans,
    ui_rescan_result,
    ui_export,
)


def test_ui_pair_documented_keys_and_mapping(seeded_conn):
    pairs = ui_pairs(seeded_conn)
    assert len(pairs) == 2
    p = pairs[0]

    expected_keys = {
        "id", "leftId", "rightId", "score", "status",
        "reason", "signals", "createdAt", "label",
        "product_a", "product_b",
    }
    assert set(p.keys()) == expected_keys

    assert p["id"] in ("X01|X02", "X03|X04")
    assert isinstance(p["leftId"], str)
    assert isinstance(p["rightId"], str)
    assert 0.0 <= p["score"] <= 1.0
    assert p["status"] == "pending"
    assert isinstance(p["reason"], str)
    assert isinstance(p["signals"], list)
    assert p["createdAt"] is not None

    expected_prod_keys = {
        "id", "title", "brand", "model", "category",
        "price", "sku", "status", "image", "updatedAt",
        "variant", "pack_quantity", "unit",
    }
    assert set(p["product_a"].keys()) == expected_prod_keys
    assert set(p["product_b"].keys()) == expected_prod_keys


def test_score_normalisation(conn):
    upsert_products(
        conn,
        [
            {"product_id": "A1", "title": "P1", "raw_json": "{}"},
            {"product_id": "A2", "title": "P2", "raw_json": "{}"},
            {"product_id": "B1", "title": "P3", "raw_json": "{}"},
            {"product_id": "B2", "title": "P4", "raw_json": "{}"},
        ],
    )
    save_suggestions(
        conn,
        [
            {"id_a": "A1", "id_b": "A2", "confidence": 95.0, "reasons": []},
            {"id_a": "B1", "id_b": "B2", "confidence": 0.88, "reasons": []},
        ],
    )
    p_95 = ui_pair(conn, "A1|A2")
    assert p_95["score"] == 0.95

    p_88 = ui_pair(conn, "B1|B2")
    assert p_88["score"] == 0.88


def test_label_generation_for_careful_review_and_missing_brand(conn):
    upsert_products(
        conn,
        [
            {"product_id": "C1", "title": "P1", "raw_json": "{}"},
            {"product_id": "C2", "title": "P2", "raw_json": "{}"},
            {"product_id": "D1", "title": "P3", "raw_json": "{}"},
            {"product_id": "D2", "title": "P4", "raw_json": "{}"},
        ],
    )
    save_suggestions(
        conn,
        [
            {
                "id_a": "C1",
                "id_b": "C2",
                "confidence": 0.85,
                "reasons": ["similar title"],
                "flags": ["Missing Brand flag"],
            },
            {
                "id_a": "D1",
                "id_b": "D2",
                "confidence": 0.70,
                "reasons": ["Careful review required due to pack conflict"],
                "flags": [],
            },
        ],
    )
    assert ui_pair(conn, "C1|C2")["label"] == "Needs careful review"
    assert ui_pair(conn, "D1|D2")["label"] == "Needs careful review"


def test_status_transitions_pending_flagged_accepted(seeded_conn):
    key = "X01|X02"
    assert ui_pair(seeded_conn, key)["status"] == "pending"

    res_flag = submit_ui_decision(
        seeded_conn, key, "flagged", note="hold on", reviewer="reviewer_bob"
    )
    assert res_flag["decision"] == "flagged"
    assert ui_pair(seeded_conn, key)["status"] == "flagged"

    res_accept = submit_ui_decision(
        seeded_conn,
        key,
        "accepted",
        note="good match",
        reviewer="reviewer_bob",
        time_spent=12.5,
    )
    assert res_accept["decision"] == "accepted"
    assert ui_pair(seeded_conn, key)["status"] == "accepted"

    row = seeded_conn.execute(
        "SELECT reviewer, time_spent_seconds, note FROM decisions WHERE pair_key = ?",
        (key,),
    ).fetchone()
    assert row["reviewer"] == "reviewer_bob"
    assert row["time_spent_seconds"] == 12.5
    assert row["note"] == "good match"


def test_submit_ui_decision_validation_and_tilde_resolution(seeded_conn):
    res = submit_ui_decision(seeded_conn, "X01~X02", "rejected", note="rejecting")
    assert res["decision"] == "rejected"
    assert res["pairId"] == "X01|X02"
    assert ui_pair(seeded_conn, "X01~X02")["status"] == "rejected"

    with pytest.raises(ValueError):
        submit_ui_decision(seeded_conn, "X03|X04", "merged")

    with pytest.raises(KeyError):
        submit_ui_decision(seeded_conn, "UNKNOWN|PAIR", "accepted")


def test_product_mapping_with_raw_json_fields_and_defaults(conn):
    prods = [
        {
            "product_id": "P10",
            "title": "Title 10",
            "brand": "Brand 10",
            "model": "M10",
            "category": "Electronics",
            "price": 2500,
            "sku": "SKU-10",
            "status": "custom-status",
            "updatedAt": "2026-10-10",
            "variant": "Red",
            "pack_quantity": 2,
            "unit": "pcs",
            "image_ref": "http://img.jpg",
        },
        {
            "product_id": "P11",
            "title": "Title 11",
            "raw_json": json.dumps({"product_id": "P11"}),
        },
    ]
    upsert_products(conn, prods)

    u_p10 = ui_product(conn, "P10")
    assert u_p10["category"] == "Electronics"
    assert u_p10["price"] == 2500
    assert u_p10["sku"] == "SKU-10"
    assert u_p10["status"] == "custom-status"
    assert u_p10["updatedAt"] == "2026-10-10"
    assert u_p10["variant"] == "Red"
    assert u_p10["pack_quantity"] == 2
    assert u_p10["unit"] == "pcs"
    assert u_p10["image"] == "http://img.jpg"

    u_p11 = ui_product(conn, "P11")
    assert u_p11["category"] is None
    assert u_p11["price"] is None
    assert u_p11["sku"] is None
    assert u_p11["status"] == "active"
    assert u_p11["updatedAt"] is None

    all_prods = ui_products(conn)
    assert len(all_prods) == 2


def test_ui_metrics_without_snapshot_and_with_snapshot(conn, sample_products, sample_suggestions):
    upsert_products(conn, sample_products)
    save_suggestions(conn, sample_suggestions)
    load_labelled_pairs(
        conn,
        [
            {"a": "X01", "b": "X02", "duplicate": 1},
            {"a": "X03", "b": "X04", "duplicate": 0},
        ],
    )
    set_setting(conn, "false_merge_cost_inr", "5000")

    m_no_snap = ui_metrics(conn)
    assert m_no_snap["totalProducts"] == 4
    assert m_no_snap["pendingReviews"] == 2
    assert m_no_snap["precision"] is None
    assert m_no_snap["recall"] is None
    assert m_no_snap["precisionCorrect"] is None
    assert m_no_snap["falseMergeRate"] is None
    assert m_no_snap["falseMergeCount"] == 0
    assert m_no_snap["falseMergeCostInr"] == 5000
    assert m_no_snap["falseMergeCostNote"] == "Assumption, not observed data"

    save_metric_snapshot(
        conn,
        source="eval",
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
    )
    m_snap = ui_metrics(conn)
    assert m_snap["precision"] == 100.0
    assert m_snap["precisionCorrect"] == 9
    assert m_snap["precisionReviewed"] == 9
    assert m_snap["recall"] == 100.0
    assert m_snap["recallFound"] == 9
    assert m_snap["recallExpected"] == 9

    submit_ui_decision(conn, "X01|X02", "accept", time_spent=20.0)
    m_acc1 = ui_metrics(conn)
    assert m_acc1["falseMergeCount"] == 0
    assert m_acc1["falseMergeRate"] == 0.0
    assert m_acc1["avgReviewTimeSeconds"] == 20.0

    submit_ui_decision(conn, "X03|X04", "accept", time_spent=10.0)
    m_acc2 = ui_metrics(conn)
    assert m_acc2["falseMergeCount"] == 1
    assert m_acc2["falseMergeRate"] == 50.0
    assert m_acc2["avgReviewTimeSeconds"] == 15.0


def test_ui_scans_and_rescan_result(conn):
    sid = start_scan_run(conn, "batch-1")
    finish_scan_run(
        conn,
        sid,
        products_count=50,
        pairs_found=12,
        new_pairs=4,
        status="completed",
    )
    scans = ui_scans(conn)
    assert len(scans) == 1
    s = scans[0]
    assert s["id"] == f"SCAN-{sid:04d}"
    assert s["source"] == "batch-1"
    assert s["products"] == 50
    assert s["pairs"] == 12
    assert s["status"] == "completed"

    res = ui_rescan_result(conn, sid)
    assert res["id"] == f"SCAN-{sid:04d}"
    assert res["status"] == "completed"
    assert "4 new pairs" in res["message"]


def test_ui_export_combinations_and_validation(seeded_conn):
    submit_ui_decision(seeded_conn, "X01|X02", "accept")

    c1, m1, f1 = ui_export(seeded_conn, "csv", "reviews")
    assert "text/csv" in m1
    assert f1 == "reviews.csv"
    assert "X01|X02" in c1

    c2, m2, f2 = ui_export(seeded_conn, "json", "reviews")
    assert m2 == "application/json"
    assert f2 == "reviews.json"
    assert json.loads(c2)[0]["pair_key"] == "X01|X02"

    c3, m3, f3 = ui_export(seeded_conn, "csv", "products")
    assert "text/csv" in m3
    assert f3 == "products.csv"
    assert "product_id" in c3

    c4, m4, f4 = ui_export(seeded_conn, "json", "products")
    assert m4 == "application/json"
    assert f4 == "products.json"
    assert len(json.loads(c4)) == 4

    with pytest.raises(ValueError):
        ui_export(seeded_conn, "xml", "reviews")

    with pytest.raises(ValueError):
        ui_export(seeded_conn, "csv", "unknown_kind")


def test_end_to_end_fixture_structure_and_restart(db_path):
    conn = get_conn(db_path)
    init_db(conn)

    products = [
        {"product_id": f"P{i:02d}", "title": f"Product {i}", "brand": "B", "raw_json": "{}"}
        for i in range(1, 21)
    ]
    upsert_products(conn, products)

    suggestions = [
        {"id_a": f"P{i:02d}", "id_b": f"P{i+1:02d}", "confidence": 0.85, "reasons": ["similar"]}
        for i in range(1, 10)
    ]
    save_suggestions(conn, suggestions)

    assert len(ui_pairs(conn)) == 9
    assert len(ui_pairs(conn, status="pending")) == 9

    submit_ui_decision(conn, "P01|P02", "accepted")
    submit_ui_decision(conn, "P02|P03", "flagged")
    submit_ui_decision(conn, "P03|P04", "rejected")

    assert len(ui_pairs(conn, status="accepted")) == 1
    assert len(ui_pairs(conn, status="flagged")) == 1
    assert len(ui_pairs(conn, status="rejected")) == 1
    assert len(ui_pairs(conn, status="pending")) == 6

    added = save_suggestions(conn, suggestions)
    assert added == 0

    conn.close()

    conn2 = get_conn(db_path)
    assert ui_pair(conn2, "P01|P02")["status"] == "accepted"
    assert ui_pair(conn2, "P02|P03")["status"] == "flagged"
    assert ui_pair(conn2, "P03|P04")["status"] == "rejected"
    assert ui_pair(conn2, "P04|P05")["status"] == "pending"
    conn2.close()
