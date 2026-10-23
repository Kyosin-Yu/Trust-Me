import csv
import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "dataset/processed/strategy_a_v1"
EXPECTED = {
    "train": (46_564, 36_431, 10_133),
    "validation": (9_938, 7_797, 2_141),
    "test": (9_926, 7_788, 2_138),
}

def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))

def main():
    manifest_path = DATA_DIR / "split_manifest.json"
    with manifest_path.open("r", encoding="utf-8") as file:
        manifest = json.load(file)
    print("=== EXPORTED DATASET VERIFICATION ===")
    all_ids = set()
    product_sets = {}
    text_sets = {}
    total = 0
    for name, (expected_total, expected_fake, expected_genuine) in EXPECTED.items():
        rows = read_csv(DATA_DIR / f"{name}.csv")
        counts = Counter(row["label"] for row in rows)
        assert len(rows) == expected_total
        assert counts["1"] == expected_fake
        assert counts["0"] == expected_genuine
        ids = {row["review_id"] for row in rows}
        assert len(ids) == len(rows)
        assert all_ids.isdisjoint(ids)
        all_ids.update(ids)
        product_sets[name] = {row["asin"] for row in rows}
        text_sets[name] = {row["review_text"] for row in rows}
        saved_summary = manifest["partitions"][name]
        assert saved_summary["reviews"] == len(rows)
        assert saved_summary["candidate_fake"] == counts["1"]
        assert saved_summary["candidate_genuine"] == counts["0"]
        assert saved_summary["unique_products"] == len(product_sets[name])
        total += len(rows)
        print(
            f"{name}: {len(rows):,} rows | "
            f"fake={counts['1']:,} | "
            f"genuine={counts['0']:,} | PASS"
        )
    names = list(EXPECTED)
    for i, first in enumerate(names):
        for second in names[i + 1:]:
            assert product_sets[first].isdisjoint(product_sets[second])
            assert text_sets[first].isdisjoint(text_sets[second])
    excluded = read_csv(DATA_DIR / "excluded_text_overlap.csv")
    assert len(excluded) == 93
    assert total == 66_428
    assert manifest["decontamination"]["candidate_reviews_after"] == total
    assert manifest["decontamination"]["excluded_reviews"] == len(excluded)
    print(f"Excluded overlap rows: {len(excluded):,} | PASS")
    print(f"Total exported rows: {total:,} | PASS")
    print("Product isolation: PASS")
    print("Exact-text isolation: PASS")
    print("Review ID uniqueness: PASS")
    print("Manifest consistency: PASS")
    print("EXPORTED DATASET VERIFICATION: PASSED")

if __name__ == "__main__":
    main()
