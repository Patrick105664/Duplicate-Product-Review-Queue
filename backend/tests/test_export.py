import csv
import io
import json

from app.db import pair_key, record_decision
from app.export import reviewed_rows, export_csv, export_json


def test_only_reviewed_pairs_appear(seeded_conn):
    assert reviewed_rows(seeded_conn) == []
    key = pair_key("X01", "X02")
    record_decision(seeded_conn, key, "accept", "alice", time_spent=3.0)
    rows = reviewed_rows(seeded_conn)
    assert len(rows) == 1
    assert rows[0]["pair_key"] == key


def test_csv_has_expected_header(seeded_conn):
    key = pair_key("X01", "X02")
    record_decision(seeded_conn, key, "reject", "bob")
    text = export_csv(seeded_conn)
    reader = csv.DictReader(io.StringIO(text))
    expected = {
        "pair_key", "id_a", "id_b", "title_a", "title_b",
        "confidence", "reasons", "flags", "decision", "reviewer",
        "note", "time_spent_seconds", "decided_at",
    }
    assert set(reader.fieldnames) == expected


def test_empty_export_returns_header(conn):
    text = export_csv(conn)
    assert text.strip() != ""
    reader = csv.DictReader(io.StringIO(text))
    assert reader.fieldnames is not None
    rows = list(reader)
    assert len(rows) == 0


def test_json_round_trips(seeded_conn):
    key = pair_key("X03", "X04")
    record_decision(seeded_conn, key, "accept", "carol", time_spent=7.5)
    text = export_json(seeded_conn)
    data = json.loads(text)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["decision"] == "accept"


def test_reasons_joined_with_semicolon(seeded_conn):
    key = pair_key("X01", "X02")
    record_decision(seeded_conn, key, "accept", "dan")
    rows = reviewed_rows(seeded_conn)
    assert "; " in rows[0]["reasons"]
    assert rows[0]["reasons"] == "same model; same brand"
