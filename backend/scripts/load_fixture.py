"""Load fixture JSON into the review database."""
import argparse
import json
import sys
from pathlib import Path

from app.db import get_conn, init_db, upsert_products, load_labelled_pairs


def main():
    parser = argparse.ArgumentParser(description="Load fixture into review DB")
    parser.add_argument("--fixture", required=True, help="Path to fixture JSON")
    parser.add_argument("--db", default=None, help="Path to SQLite DB")
    args = parser.parse_args()

    fixture_path = Path(args.fixture)
    if not fixture_path.exists():
        print(f"Error: fixture file not found: {fixture_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(fixture_path.read_text())
    products = data["records"]["products"]
    pairs = data["records"].get("labelled_pairs", [])

    seen_ids = set()
    for p in products:
        pid = p.get("product_id")
        if not pid:
            print("Error: product missing product_id", file=sys.stderr)
            sys.exit(1)
        if pid in seen_ids:
            print(f"Error: duplicate product_id in fixture: {pid}", file=sys.stderr)
            sys.exit(1)
        seen_ids.add(pid)

    conn = get_conn(args.db)
    init_db(conn)
    upsert_products(conn, products)
    load_labelled_pairs(conn, pairs)
    conn.close()

    print(f"Loaded {len(products)} products, {len(pairs)} labelled pairs.")


if __name__ == "__main__":
    main()
