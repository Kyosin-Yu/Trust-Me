import csv
import io
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "dataset/raw/public_reviews_dataset_cleaned.csv_.zip"
CSV_NAME = "public_reviews_dataset_cleaned.csv"


def main():
    reviewer_counts = Counter()
    product_counts = Counter()

    with zipfile.ZipFile(ZIP_PATH) as archive:
        with archive.open(CSV_NAME) as file:
            reader = csv.DictReader(
                io.TextIOWrapper(file, encoding="utf-8-sig", newline="")
            )

            for row in reader:
                reviewer_id = (row["reviewer_id"] or "").strip()
                asin = (row["asin"] or "").strip()

                if reviewer_id:
                    reviewer_counts[reviewer_id] += 1

                if asin:
                    product_counts[asin] += 1

    repeated_reviewers = sum(
        count > 1 for count in reviewer_counts.values()
    )
    repeated_products = sum(
        count > 1 for count in product_counts.values()
    )

    reviewer_extra_rows = sum(
        count - 1 for count in reviewer_counts.values() if count > 1
    )
    product_extra_rows = sum(
        count - 1 for count in product_counts.values() if count > 1
    )

    print("=== GROUP LEAKAGE AUDIT ===")
    print(f"Unique reviewers: {len(reviewer_counts):,}")
    print(f"Reviewers with multiple reviews: {repeated_reviewers:,}")
    print(f"Extra rows from repeated reviewers: {reviewer_extra_rows:,}")
    print(f"Maximum reviews by one reviewer: {max(reviewer_counts.values(), default=0):,}")
    print(f"Unique products: {len(product_counts):,}")
    print(f"Products with multiple reviews: {repeated_products:,}")
    print(f"Extra rows from repeated products: {product_extra_rows:,}")
    print(f"Maximum reviews for one product: {max(product_counts.values(), default=0):,}")


if __name__ == "__main__":
    main()
