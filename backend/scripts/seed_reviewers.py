import argparse

from app.db import get_conn, init_db
from app.reviewers import create_reviewer, get_reviewer_by_username

_DEMO_ACCOUNTS = [
    {"username": "alice", "role": "reviewer", "display_name": "Alice"},
    {"username": "bob", "role": "reviewer", "display_name": "Bob"},
    {"username": "admin", "role": "admin", "display_name": "Admin"},
]
_DEMO_PASS = "demo-pass-123"


def seed(db_path: str | None = None) -> None:
    print("DEMO CREDENTIALS ONLY - NOT FOR PRODUCTION USE")
    conn = get_conn(db_path)
    init_db(conn)
    for acct in _DEMO_ACCOUNTS:
        existing = get_reviewer_by_username(conn, acct["username"])
        if existing:
            print(f"Skipped existing reviewer: {acct['username']}")
        else:
            create_reviewer(
                conn,
                username=acct["username"],
                password=_DEMO_PASS,
                display_name=acct["display_name"],
                role=acct["role"],
            )
            print(f"Created reviewer: {acct['username']}")
    conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed initial demo reviewer accounts")
    parser.add_argument("--db", default=None, help="Path to SQLite database file")
    args = parser.parse_args()
    seed(args.db)


if __name__ == "__main__":
    main()
