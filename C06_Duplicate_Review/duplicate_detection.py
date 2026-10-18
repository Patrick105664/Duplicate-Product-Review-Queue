
import json
from evaluation import evaluate_pairs


with open("fixture.json", "r", encoding="utf-8") as file:
    data = json.load(file)

products = {
    product["product_id"]: product
    for product in data["records"]["products"]
}

labelled_pairs = data["records"]["labelled_pairs"]

results = evaluate_pairs(labelled_pairs, products)

print("\nDUPLICATE PRODUCT DETECTION")
print("=" * 40)

print("Total labelled pairs:", results["total"])
print("True Positives (TP):", results["TP"])
print("False Positives (FP):", results["FP"])
print("True Negatives (TN):", results["TN"])
print("False Negatives (FN):", results["FN"])

print(f'Precision: {results["precision"]:.2%}')
print(f'Recall:    {results["recall"]:.2%}')
print(f'Accuracy:  {results["accuracy"]:.2%}')

print("\nDetailed evidence saved to results.csv")
