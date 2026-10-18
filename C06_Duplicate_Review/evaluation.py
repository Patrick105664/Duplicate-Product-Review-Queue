
import csv
from matching_engine import compare_products


def evaluate_pairs(labelled_pairs, products):
    tp = fp = tn = fn = 0
    rows = []

    for pair in labelled_pairs:
        a = products[pair["a"]]
        b = products[pair["b"]]

        actual = pair["duplicate"]
        result = compare_products(a, b)
        predicted = result["predicted_duplicate"]

        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and not actual:
            tn += 1
        else:
            fn += 1

        rows.append({
            "product_a": pair["a"],
            "product_b": pair["b"],
            "actual_duplicate": actual,
            "predicted_duplicate": predicted,
            "similarity_score": result["similarity_score"],
            "evidence": "; ".join(result["evidence"]),
            "conflicts": "; ".join(result["conflicts"]),
            "correct": actual == predicted
        })

    total = tp + fp + tn + fn
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    accuracy = (tp + tn) / total if total else 0

    columns = [
        "product_a",
        "product_b",
        "actual_duplicate",
        "predicted_duplicate",
        "similarity_score",
        "evidence",
        "conflicts",
        "correct"
    ]

    with open("results.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    return {
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "total": total,
        "precision": precision,
        "recall": recall,
        "accuracy": accuracy
    }
