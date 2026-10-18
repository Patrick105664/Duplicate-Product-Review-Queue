import pytest
from app.db import get_conn, init_db, upsert_products, save_suggestions


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_review.db")


@pytest.fixture
def conn(db_path):
    c = get_conn(db_path)
    init_db(c)
    yield c
    c.close()


@pytest.fixture
def sample_products():
    return [
        {"product_id": "X01", "brand": "Demo", "model": "M1",
         "pack_quantity": 1, "size": "M", "title": "Sample 1"},
        {"product_id": "X02", "brand": "Demo", "model": "M1",
         "pack_quantity": 1, "size": "M", "title": "Sample 1"},
        {"product_id": "X03", "brand": "Demo", "model": "M2",
         "pack_quantity": None, "size": "L", "title": "Sample 2"},
        {"product_id": "X04", "brand": "Demo", "model": "M2",
         "pack_quantity": 1, "size": "L", "title": "Sample 2"},
    ]


@pytest.fixture
def sample_suggestions():
    return [
        {"id_a": "X02", "id_b": "X01", "confidence": 0.95,
         "reasons": ["same model", "same brand"]},
        {"id_a": "X03", "id_b": "X04", "confidence": 0.88,
         "reasons": ["same model"], "flags": ["pack mismatch"]},
    ]


@pytest.fixture
def seeded_conn(conn, sample_products, sample_suggestions):
    upsert_products(conn, sample_products)
    save_suggestions(conn, sample_suggestions)
    return conn
