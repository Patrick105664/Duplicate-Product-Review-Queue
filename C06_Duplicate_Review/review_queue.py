
import csv
import json
import os

SUGGESTIONS_FILE = "duplicate_suggestions.csv"
DECISIONS_FILE = "review_decisions.json"


def load_decisions():
    if not os.path.exists(DECISIONS_FILE):
        return {}

    with open(DECISIONS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_decisions(decisions):
    with open(DECISIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(decisions, file, indent=4)


def load_suggestions():
    with open(SUGGESTIONS_FILE, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def main():
    suggestions = load_suggestions()
    decisions = load_decisions()

    print("\nDUPLICATE PRODUCT REVIEW QUEUE")
    print("=" * 40)

    pending = [
        row for row in suggestions
        if row["product_a"] + "|" + row["product_b"] not in decisions
    ]

    print("Total suggestions:", len(suggestions))
    print("Previously reviewed:", len(suggestions) - len(pending))
    print("Pending review:", len(pending))

    for row in pending:
        key = row["product_a"] + "|" + row["product_b"]

        print("\nProduct A:", row["product_a"], "-", row["title_a"])
        print("Product B:", row["product_b"], "-", row["title_b"])
        print("Similarity:", row["similarity_score"])
        print("Evidence:", row["evidence"])
        print("Conflicts:", row["conflicts"] or "None")

        while True:
            choice = input("Decision: [A]ccept / [R]eject / [S]kip / [Q]uit: ")
            choice = choice.strip().upper()

            if choice in ("A", "R", "S", "Q"):
                break

            print("Please enter A, R, S, or Q.")

        if choice == "Q":
            break

        if choice == "S":
            continue

        decisions[key] = {
            "product_a": row["product_a"],
            "product_b": row["product_b"],
            "decision": "accepted" if choice == "A" else "rejected",
            "evidence": row["evidence"],
            "similarity_score": row["similarity_score"]
        }

        save_decisions(decisions)
        print("Decision saved.")

    print("\nReview session finished.")
    print("Saved decisions:", len(decisions))
    print("File:", DECISIONS_FILE)


if __name__ == "__main__":
    main()
