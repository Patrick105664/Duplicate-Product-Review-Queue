import sqlite3
import pytest

from app.db import get_conn, init_db, record_decision, upsert_products, save_suggestions
from app.evaluation import reviewer_stats
from app.reviewers import (
    hash_password,
    verify_password,
    create_reviewer,
    get_reviewer,
    get_reviewer_by_username,
    list_reviewers,
    set_reviewer_active,
    authenticate,
    create_session,
    get_session_reviewer,
    delete_session,
)


def test_hash_password_produces_different_hashes_and_no_plain_text():
    h1 = hash_password("secretpassword")
    h2 = hash_password("secretpassword")
    assert h1 != h2
    assert "secretpassword" not in h1
    assert h1.startswith("scrypt$16384$8$1$")


def test_verify_password_accepts_correct_rejects_wrong_and_malformed():
    h = hash_password("mypassword123")
    assert verify_password("mypassword123", h) is True
    assert verify_password("wrongpassword", h) is False
    assert verify_password("mypassword123", "malformed_string") is False
    assert verify_password("mypassword123", "") is False
    assert verify_password("mypassword123", "scrypt$abc$def") is False
    assert verify_password("mypassword123", "scrypt$16384$8$1$bad$hex") is False


def test_create_reviewer_normalises_and_no_hash_in_dict(conn):
    user = create_reviewer(conn, "  Alice_Smith  ", "password123", display_name="Alice S")
    assert user["username"] == "alice_smith"
    assert user["display_name"] == "Alice S"
    assert user["role"] == "reviewer"
    assert user["is_active"] == 1
    assert "password_hash" not in user


def test_create_reviewer_duplicate_username_raises(conn):
    create_reviewer(conn, "bob", "password123")
    with pytest.raises(ValueError, match="username already exists"):
        create_reviewer(conn, "  Bob  ", "differentpassword123")


def test_create_reviewer_invalid_inputs_raise(conn):
    with pytest.raises(ValueError):
        create_reviewer(conn, "charlie", "short")
    with pytest.raises(ValueError):
        create_reviewer(conn, "   ", "password123")
    with pytest.raises(ValueError):
        create_reviewer(conn, "dave", "password123", role="superadmin")


def test_authenticate_success_wrong_pass_unknown_and_inactive(conn):
    u = create_reviewer(conn, "eve", "correctpass123")
    auth_ok = authenticate(conn, "eve", "correctpass123")
    assert auth_ok is not None
    assert auth_ok["username"] == "eve"
    assert "password_hash" not in auth_ok

    assert authenticate(conn, "eve", "wrongpass123") is None
    assert authenticate(conn, "nonexistent", "correctpass123") is None

    set_reviewer_active(conn, u["reviewer_id"], False)
    assert authenticate(conn, "eve", "correctpass123") is None


def test_set_reviewer_active_and_unknown_keyerror(conn):
    u = create_reviewer(conn, "frank", "password123")
    set_reviewer_active(conn, u["reviewer_id"], False)
    assert authenticate(conn, "frank", "password123") is None

    with pytest.raises(KeyError):
        create_session(conn, u["reviewer_id"])

    with pytest.raises(KeyError):
        set_reviewer_active(conn, 999999, False)


def test_create_session_and_token_not_stored_plain(conn):
    u = create_reviewer(conn, "grace", "password123")
    token = create_session(conn, u["reviewer_id"])
    assert isinstance(token, str) and len(token) > 0

    rows = conn.execute("SELECT * FROM sessions").fetchall()
    assert len(rows) == 1
    assert token not in rows[0]["token_hash"]

    resolved = get_session_reviewer(conn, token)
    assert resolved is not None
    assert resolved["username"] == "grace"
    assert "password_hash" not in resolved


def test_expired_session_returns_none_and_is_removed(conn):
    u = create_reviewer(conn, "heidi", "password123")
    token = create_session(conn, u["reviewer_id"], ttl_hours=-1)
    assert get_session_reviewer(conn, token) is None

    remaining = conn.execute("SELECT COUNT(*) AS c FROM sessions").fetchone()["c"]
    assert remaining == 0


def test_delete_session_logout(conn):
    u = create_reviewer(conn, "ivan", "password123")
    token = create_session(conn, u["reviewer_id"])
    delete_session(conn, token)
    assert get_session_reviewer(conn, token) is None
    # calling again should be safe and not raise
    delete_session(conn, token)


def test_session_stops_working_when_reviewer_deactivated(conn):
    u = create_reviewer(conn, "judy", "password123")
    token = create_session(conn, u["reviewer_id"])
    assert get_session_reviewer(conn, token) is not None

    set_reviewer_active(conn, u["reviewer_id"], False)
    assert get_session_reviewer(conn, token) is None


def test_record_decision_with_reviewer_id(seeded_conn):
    u = create_reviewer(seeded_conn, "karl", "password123")
    key = "X01|X02"
    record_decision(
        seeded_conn,
        key,
        "accept",
        "wrong_name_passed",
        reviewer_id=u["reviewer_id"],
    )

    row = seeded_conn.execute(
        "SELECT reviewer, reviewer_id FROM decisions WHERE pair_key = ?", (key,)
    ).fetchone()
    assert row["reviewer"] == "karl"
    assert row["reviewer_id"] == u["reviewer_id"]

    log_row = seeded_conn.execute(
        "SELECT reviewer, reviewer_id FROM decision_log WHERE pair_key = ?", (key,)
    ).fetchone()
    assert log_row["reviewer"] == "karl"
    assert log_row["reviewer_id"] == u["reviewer_id"]


def test_record_decision_reviewer_id_validation(seeded_conn):
    u = create_reviewer(seeded_conn, "laura", "password123")
    set_reviewer_active(seeded_conn, u["reviewer_id"], False)

    with pytest.raises(ValueError):
        record_decision(
            seeded_conn, "X01|X02", "accept", "laura", reviewer_id=u["reviewer_id"]
        )

    with pytest.raises(KeyError):
        record_decision(
            seeded_conn, "X01|X02", "accept", "nobody", reviewer_id=999999
        )

    # Without reviewer_id works as before with free-text name
    record_decision(seeded_conn, "X01|X02", "accept", "free_agent")
    row = seeded_conn.execute(
        "SELECT reviewer, reviewer_id FROM decisions WHERE pair_key = 'X01|X02'"
    ).fetchone()
    assert row["reviewer"] == "free_agent"
    assert row["reviewer_id"] is None


def test_decision_with_reviewer_id_survives_restart(db_path, sample_products, sample_suggestions):
    conn = get_conn(db_path)
    init_db(conn)
    upsert_products(conn, sample_products)
    save_suggestions(conn, sample_suggestions)
    u = create_reviewer(conn, "mallory", "password123")
    record_decision(conn, "X01|X02", "accept", "any", reviewer_id=u["reviewer_id"])
    conn.close()

    conn2 = get_conn(db_path)
    row = conn2.execute(
        "SELECT reviewer, reviewer_id FROM decisions WHERE pair_key = 'X01|X02'"
    ).fetchone()
    assert row["reviewer"] == "mallory"
    assert row["reviewer_id"] == u["reviewer_id"]
    conn2.close()


def test_migration_from_old_database(tmp_path):
    old_db = str(tmp_path / "old.db")
    conn = sqlite3.connect(old_db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript("""
        CREATE TABLE products (
            product_id TEXT PRIMARY KEY, title TEXT, brand TEXT, model TEXT,
            variant TEXT, pack_quantity INTEGER, unit TEXT, image_ref TEXT, raw_json TEXT NOT NULL
        );
        CREATE TABLE suggestions (
            pair_key TEXT PRIMARY KEY, id_a TEXT NOT NULL, id_b TEXT NOT NULL,
            confidence REAL NOT NULL, reasons_json TEXT NOT NULL,
            flags_json TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL
        );
        CREATE TABLE decisions (
            pair_key TEXT PRIMARY KEY REFERENCES suggestions(pair_key),
            decision TEXT NOT NULL, reviewer TEXT NOT NULL, note TEXT,
            time_spent_seconds REAL, decided_at TEXT NOT NULL
        );
        CREATE TABLE decision_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, pair_key TEXT NOT NULL,
            decision TEXT NOT NULL, reviewer TEXT NOT NULL, decided_at TEXT NOT NULL
        );
        INSERT INTO products VALUES ('A', 't', 'b', 'm', 'v', 1, 'u', 'img', '{}');
        INSERT INTO products VALUES ('B', 't', 'b', 'm', 'v', 1, 'u', 'img', '{}');
        INSERT INTO suggestions VALUES ('A|B', 'A', 'B', 0.9, '[]', '[]', '2026-01-01');
        INSERT INTO decisions VALUES ('A|B', 'accept', 'legacy_reviewer', 'note', 15.0, '2026-01-01');
        INSERT INTO decision_log VALUES (1, 'A|B', 'accept', 'legacy_reviewer', '2026-01-01');
    """)
    conn.commit()

    init_db(conn)

    cols_dec = {r["name"] for r in conn.execute("PRAGMA table_info(decisions)").fetchall()}
    assert "reviewer_id" in cols_dec
    cols_log = {r["name"] for r in conn.execute("PRAGMA table_info(decision_log)").fetchall()}
    assert "reviewer_id" in cols_log

    row = conn.execute("SELECT * FROM decisions WHERE pair_key = 'A|B'").fetchone()
    assert row["reviewer"] == "legacy_reviewer"
    assert row["reviewer_id"] is None

    # Idempotent: calling init_db again changes nothing
    init_db(conn)
    row2 = conn.execute("SELECT * FROM decisions WHERE pair_key = 'A|B'").fetchone()
    assert row2["reviewer"] == "legacy_reviewer"
    assert row2["reviewer_id"] is None
    conn.close()


def test_reviewer_stats_counts_and_averages(seeded_conn):
    r1 = create_reviewer(seeded_conn, "rev1", "password123")
    r2 = create_reviewer(seeded_conn, "rev2", "password123")

    record_decision(
        seeded_conn, "X01|X02", "accept", "ignored", time_spent=10.0, reviewer_id=r1["reviewer_id"]
    )
    record_decision(
        seeded_conn, "X03|X04", "reject", "ignored", time_spent=20.0, reviewer_id=r2["reviewer_id"]
    )

    upsert_products(
        seeded_conn,
        [
            {"product_id": "X05", "title": "P5", "raw_json": "{}"},
            {"product_id": "X06", "title": "P6", "raw_json": "{}"},
        ],
    )
    save_suggestions(
        seeded_conn,
        [{"id_a": "X05", "id_b": "X06", "confidence": 0.7, "reasons": []}],
    )
    record_decision(
        seeded_conn, "X05|X06", "accept", "anon", time_spent=None, reviewer_id=None
    )

    stats = reviewer_stats(seeded_conn)
    stats_map = {s["username"]: s for s in stats}

    assert "rev1" in stats_map
    assert stats_map["rev1"]["accepts"] == 1
    assert stats_map["rev1"]["rejects"] == 0
    assert stats_map["rev1"]["total"] == 1
    assert stats_map["rev1"]["avg_seconds"] == 10.0

    assert "rev2" in stats_map
    assert stats_map["rev2"]["accepts"] == 0
    assert stats_map["rev2"]["rejects"] == 1
    assert stats_map["rev2"]["total"] == 1
    assert stats_map["rev2"]["avg_seconds"] == 20.0

    assert "(unattributed)" in stats_map
    assert stats_map["(unattributed)"]["accepts"] == 1
    assert stats_map["(unattributed)"]["rejects"] == 0
    assert stats_map["(unattributed)"]["total"] == 1
    assert stats_map["(unattributed)"]["avg_seconds"] is None


def test_foreign_key_enforcement_direct_sql_fails(seeded_conn):
    with pytest.raises(sqlite3.IntegrityError):
        seeded_conn.execute(
            """
            INSERT INTO decisions (pair_key, decision, reviewer, decided_at, reviewer_id)
            VALUES ('X01|X02', 'accept', 'direct', '2026-01-01', 999999)
            """
        )
