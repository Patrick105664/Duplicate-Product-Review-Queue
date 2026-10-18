
import re
from difflib import SequenceMatcher

TITLE_SIMILARITY_THRESHOLD = 0.90


def normalize_title(title):
    """Normalize harmless punctuation, case, and spacing differences."""
    title = (title or "").casefold().strip()
    title = re.sub(r"[^a-z0-9]+", " ", title)
    return " ".join(title.split())


def normalize_attribute(value):
    """Normalize textual attributes without changing their meaning."""
    if value is None:
        return None
    if isinstance(value, str):
        return " ".join(value.casefold().split())
    return value


def extract_storage_capacity(title):
    """Extract storage capacities such as 128GB and 1 TB."""
    title = (title or "").casefold()

    matches = re.findall(
        r"\b(\d+(?:\.\d+)?)\s*(mb|gb|tb)\b",
        title,
    )

    if not matches:
        return None

    capacities = set()

    for amount, unit in matches:
        amount = float(amount)

        # Convert capacities to a common unit for comparison.
        multipliers = {
            "mb": 1,
            "gb": 1000,
            "tb": 1000000,
        }

        capacities.add(amount * multipliers[unit])

    # Multiple distinct capacities in one title are ambiguous.
    if len(capacities) != 1:
        return None

    return capacities.pop()


def compare_products(product_a, product_b):
    evidence = []
    conflicts = []

    title_a = normalize_title(product_a.get("title"))
    title_b = normalize_title(product_b.get("title"))

    title_score = (
        SequenceMatcher(None, title_a, title_b).ratio()
        if title_a and title_b
        else 0.0
    )

    if title_a and title_a == title_b:
        evidence.append("Normalized titles match")
    elif title_score >= TITLE_SIMILARITY_THRESHOLD:
        evidence.append(f"High title similarity: {title_score:.0%}")
    else:
        evidence.append(f"Title similarity: {title_score:.0%}")

    # Explicitly detect conflicting storage capacities in titles.
    capacity_a = extract_storage_capacity(product_a.get("title"))
    capacity_b = extract_storage_capacity(product_b.get("title"))

    if capacity_a is not None and capacity_b is not None:
        if capacity_a == capacity_b:
            evidence.append("Storage capacities match")
        else:
            conflicts.append("Storage capacities differ")

    attributes = [
        ("brand", "Brands differ"),
        ("model", "Models differ"),
        ("pack_quantity", "Pack quantities differ"),
        ("size", "Sizes differ"),
    ]

    for field, conflict_message in attributes:
        value_a = normalize_attribute(product_a.get(field))
        value_b = normalize_attribute(product_b.get(field))

        if value_a is None or value_b is None:
            continue

        if value_a == "" or value_b == "":
            continue

        if value_a == value_b:
            evidence.append(f"{field.replace('_', ' ').title()} match")
        else:
            conflicts.append(conflict_message)

    predicted = (
        bool(title_a)
        and bool(title_b)
        and title_score >= TITLE_SIMILARITY_THRESHOLD
        and not conflicts
    )

    return {
        "predicted_duplicate": predicted,
        "similarity_score": round(title_score, 3),
        "evidence": evidence,
        "conflicts": conflicts,
    }


def predict_duplicate(product_a, product_b):
    return compare_products(product_a, product_b)["predicted_duplicate"]
