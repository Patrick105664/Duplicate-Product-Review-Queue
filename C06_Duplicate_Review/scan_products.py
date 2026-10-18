
import csv
import json
from itertools import combinations
from matching_engine import compare_products


# Load product data
with open("fixture.json", "r", encoding="utf-8") as file:
    data = json.load(file)

products = data["records"]["products"]

suggestions = []

# Compare every unique pair
for product_a, product_b in combinations(products, 2):
    result = compare_products(product_a, product_b)

    if result["predicted_duplicate"]:
        suggestions.append({
            "product_a": product_a["product_id"],
            "title_a": product_a.get("title", ""),
            "product_b": product_b["product_id"],
            "title_b": product_b.get("title", ""),
            "similarity_score": result["similarity_score"],
            "evidence": "; ".join(result["evidence"]),
            "conflicts": "; ".join(result["conflicts"]),
            "review_status": "Pending review"
        })

# Export suggestions
columns = [
    "product_a",
    "title_a",
    "product_b",
    "title_b",
    "similarity_score",
    "evidence",
    "conflicts",
    "review_status"
]

with open("duplicate_suggestions.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(suggestions)

total_pairs = len(products) * (len(products) - 1) // 2

print("\nFULL CATALOGUE SCAN")
print("=" * 35)
print("Products scanned:", len(products))
print("Total possible pairs:", total_pairs)
print("Duplicate suggestions:", len(suggestions))
print("Pending reviewer approval:", len(suggestions))
print("Saved to duplicate_suggestions.csv")
