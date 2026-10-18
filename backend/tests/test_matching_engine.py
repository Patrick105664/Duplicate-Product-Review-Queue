import sys
from pathlib import Path

CORE_DIR = Path(__file__).resolve().parents[2] / "C06_Duplicate_Review"
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

from matching_engine import compare_products


def product(title, brand="Demo", model="M1", pack_quantity=1, size="M"):
    return {
        "title": title,
        "brand": brand,
        "model": model,
        "pack_quantity": pack_quantity,
        "size": size,
    }


def test_exact_duplicate_is_detected():
    result = compare_products(
        product("Apple iPhone 15 128GB"),
        product("Apple iPhone 15 128GB"),
    )
    assert result["predicted_duplicate"] is True


def test_punctuation_and_spacing_difference_is_detected():
    result = compare_products(
        product("Apple iPhone 15 128GB"),
        product("Apple iPhone 15 - 128 GB"),
    )
    assert result["predicted_duplicate"] is True


def test_different_brands_are_not_duplicates():
    result = compare_products(
        product("Wireless Headphones", brand="Brand A"),
        product("Wireless Headphones", brand="Brand B"),
    )
    assert result["predicted_duplicate"] is False
    assert "Brands differ" in result["conflicts"]


def test_different_models_are_not_duplicates():
    result = compare_products(
        product("Sample Phone", model="M1"),
        product("Sample Phone", model="M2"),
    )
    assert result["predicted_duplicate"] is False
    assert "Models differ" in result["conflicts"]


def test_different_pack_quantities_are_not_duplicates():
    result = compare_products(
        product("Sample Product", pack_quantity=1),
        product("Sample Product", pack_quantity=2),
    )
    assert result["predicted_duplicate"] is False
    assert "Pack quantities differ" in result["conflicts"]


def test_different_sizes_are_not_duplicates():
    result = compare_products(
        product("Sample Shirt", size="M"),
        product("Sample Shirt", size="L"),
    )
    assert result["predicted_duplicate"] is False
    assert "Sizes differ" in result["conflicts"]


def test_similarity_score_is_not_presented_as_probability():
    result = compare_products(
        product("Apple iPhone 15 128GB"),
        product("Apple iPhone 15 - 128 GB"),
    )
    assert 0.0 <= result["similarity_score"] <= 1.0
    assert isinstance(result["evidence"], list)
    assert isinstance(result["conflicts"], list)



def test_empty_titles_are_not_duplicates():
    result = compare_products(product(""), product(""))
    assert result["predicted_duplicate"] is False


def test_missing_titles_are_not_duplicates():
    result = compare_products(product(None), product(None))
    assert result["predicted_duplicate"] is False


def test_different_products_with_similar_titles_are_not_duplicates():
    result = compare_products(
        product("Apple iPhone 15 128GB"),
        product("Apple iPhone 15 256GB"),
    )
    assert result["predicted_duplicate"] is False


def test_missing_attributes_do_not_create_conflicts():
    result = compare_products(
        product("Apple iPhone 15 128GB", brand=None, model=None),
        product("Apple iPhone 15 128GB", brand=None, model=None),
    )
    assert result["predicted_duplicate"] is True


def test_similarity_score_is_zero_for_empty_titles():
    result = compare_products(product(""), product(""))
    assert result["similarity_score"] == 0.0
