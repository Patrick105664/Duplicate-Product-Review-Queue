import pytest

from app.db import get_conn, init_db, get_pending, record_decision
from app.flags import flag_pair, get_latest_flag, list_flagged_keys


def test_flag_pair_does_not_decide_and_keeps_in_pending(seeded_conn):
    res = flag_pair(seeded_conn, "X01|X02", "alice", note="Investigate multipack")
    assert res["pair_key"] == "X01|X02"
    assert res["reviewer"] == "alice"
    assert res["note"] == "Investigate multipack"
    assert res["flagged_at"] is not None

    row = seeded_conn.execute(
        "SELECT * FROM decisions WHERE pair_key = 'X01|X02'"
    ).fetchone()
    assert row is None

    pending = get_pending(seeded_conn)
    pending_keys = {p["pair_key"] for p in pending}
    assert "X01|X02" in pending_keys


def test_flag_unknown_key_raises_keyerror(seeded_conn):
    with pytest.raises(KeyError):
        flag_pair(seeded_conn, "UNKNOWN|KEY", "bob")


def test_list_flagged_keys_and_decision_resolution(seeded_conn):
    flag_pair(seeded_conn, "X01|X02", "alice", note="note 1")
    flag_pair(seeded_conn, "X03|X04", "bob", note="note 2")

    flagged = list_flagged_keys(seeded_conn)
    assert flagged == {"X01|X02", "X03|X04"}

    record_decision(seeded_conn, "X01|X02", "accept", "alice")
    flagged_after = list_flagged_keys(seeded_conn)
    assert flagged_after == {"X03|X04"}


def test_latest_flag_wins(seeded_conn):
    flag_pair(seeded_conn, "X01|X02", "alice", note="initial")
    flag_pair(seeded_conn, "X01|X02", "bob", note="updated")

    latest = get_latest_flag(seeded_conn, "X01|X02")
    assert latest is not None
    assert latest["reviewer"] == "bob"
    assert latest["note"] == "updated"


def test_flags_survive_restart(db_path, sample_products, sample_suggestions):
    conn1 = get_conn(db_path)
    init_db(conn1)
    from app.db import upsert_products, save_suggestions
    upsert_products(conn1, sample_products)
    save_suggestions(conn1, sample_suggestions)

    flag_pair(conn1, "X01|X02", "charlie", note="persistent flag")
    conn1.close()

    conn2 = get_conn(db_path)
    flag = get_latest_flag(conn2, "X01|X02")
    assert flag is not None
    assert flag["reviewer"] == "charlie"
    assert flag["note"] == "persistent flag"
    conn2.close()
