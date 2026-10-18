from app.db import get_conn, init_db

conn = get_conn()
init_db(conn)
for t in ("pair_flags", "decisions", "decision_log", "suggestions", "scan_runs"):
    conn.execute(f"DELETE FROM {t}")
conn.commit()
print("demo state cleared (products, labelled pairs, reviewers and metric snapshots kept)")