import csv
import zipfile
from collections import Counter
from pathlib import Path

# Resolve paths from the project root, independent of terminal location.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = (
    PROJECT_ROOT
    / "dataset"
    / "raw"
    / "public_reviews_dataset_cleaned.csv_.zip"
)
CSV_NAME = "public_reviews_dataset_cleaned.csv"


def main():
    review_ids = Counter()
    review_texts = Counter()
    reviewer_ids = set()
    product_ids = set()

    total_reviews = 0

    with zipfile.ZipFile(DATASET_PATH) as archive:
        with archive.open(CSV_NAME) as file:
            import io
            reader = csv.DictReader(
                io.TextIOWrapper(
                    file, encoding="utf-8-sig", newline=""
                )
            )
            for row in reader:
                total_reviews += 1
                review_id = (row["review_id"] or "").strip()
                review_text = (row["review_text"] or "").strip()
                reviewer_id = (row["reviewer_id"] or "").strip()
                product_id = (row["asin"] or "").strip()
                review_ids[review_id] += 1
                review_texts[review_text] += 1
                if reviewer_id:
                    reviewer_ids.add(reviewer_id)
                if product_id:
                    product_ids.add(product_id)
    duplicate_id_groups = sum(
        1 for count in review_ids.values() if count > 1
    )
    duplicate_id_extra_rows = sum(
        count - 1 for count in review_ids.values() if count > 1
    )

    duplicate_text_groups = sum(
        1 for count in review_texts.values() if count > 1
    )
    duplicate_text_extra_rows = sum(
        count - 1 for count in review_texts.values() if count > 1
    )

    print("=== TRUST ME: DATASET DUPLICATE AUDIT ===")
    print(f"Total reviews: {total_reviews:,}")
    print(f"Unique review IDs: {len(review_ids):,}")
    print(f"Duplicate review ID groups: {duplicate_id_groups:,}")
    print(f"Extra rows with duplicate review IDs: {duplicate_id_extra_rows:,}")
    print(f"Unique review texts: {len(review_texts):,}")
    print(f"Duplicate text groups: {duplicate_text_groups:,}")
    print(f"Extra rows with duplicate text: {duplicate_text_extra_rows:,}")
    print(f"Unique reviewers: {len(reviewer_ids):,}")
    print(f"Unique products (ASIN): {len(product_ids):,}")

if __name__ == "__main__":
    main()
