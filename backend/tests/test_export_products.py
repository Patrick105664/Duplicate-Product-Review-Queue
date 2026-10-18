import csv
import io
import json

from app.export import export_products_csv, export_products_json


def test_export_products_csv_empty(conn):
    csv_str = export_products_csv(conn)
    lines = csv_str.strip().splitlines()
    assert len(lines) == 1
    assert lines[0] == "product_id,title,brand,model,variant,pack_quantity,unit,image_ref"


def test_export_products_csv_with_data_and_nulls(seeded_conn):
    csv_str = export_products_csv(seeded_conn)
    reader = csv.DictReader(io.StringIO(csv_str))
    rows = list(reader)
    assert len(rows) == 4

    expected_cols = [
        "product_id", "title", "brand", "model",
        "variant", "pack_quantity", "unit", "image_ref",
    ]
    assert reader.fieldnames == expected_cols

    x03 = [r for r in rows if r["product_id"] == "X03"][0]
    assert x03["pack_quantity"] == ""
    assert x03["unit"] == ""


def test_export_products_json_roundtrip_and_nulls(seeded_conn):
    json_str = export_products_json(seeded_conn)
    data = json.loads(json_str)
    assert len(data) == 4

    x03 = [r for r in data if r["product_id"] == "X03"][0]
    assert x03["product_id"] == "X03"
    assert x03["pack_quantity"] is None
    assert x03["unit"] is None
