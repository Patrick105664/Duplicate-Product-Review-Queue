
import csv
import json
import os

SUGGESTIONS_FILE = "duplicate_suggestions.csv"
DECISIONS_FILE = "review_decisions.json"
OUTPUT_FILE = "reviewed_queue.csv"


def load_decisions():
    if not os.path.exists(DECISIONS_FILE):
        return {}

    with open(DECISIONS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    decisions = load_decisions()

    with open(
        SUGGESTIONS_FILE, "r", newline="", encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        columns = list(reader.fieldnames or [])

    if "review_status" not in columns:
        columns.append("review_status")

    for row in rows:
        key = row["product_a"] + "|" + row["product_b"]

        if key in decisions:
            row["review_status"] = decisions[key]["decision"]
        else:
            row["review_status"] = "pending"

    with open(
        OUTPUT_FILE, "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    accepted = sum(
        row["review_status"] == "accepted" for row in rows
    )
    rejected = sum(
        row["review_status"] == "rejected" for row in rows
    )
    pending = sum(
        row["review_status"] == "pending" for row in rows
    )

    print("\nREVIEW QUEUE EXPORT")
    print("=" * 35)
    print("Total suggestions:", len(rows))
    print("Accepted:", accepted)
    print("Rejected:", rejected)
    print("Pending:", pending)
    print("Exported file:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
