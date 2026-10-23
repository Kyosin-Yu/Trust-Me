import csv
import io
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "dataset/raw/public_reviews_dataset_cleaned.csv_.zip"
CSV_NAME = "public_reviews_dataset_cleaned.csv"


def candidate_label(row):
    fake_product = row["fake_review_product"] == "True"
    fake_reviewer = row["reviewer_classified_fake"] == "True"
    honest_reviewer = row["reviewer_classified_honest"] == "True"
    five_star = row["review_rating"] == "5"

    if fake_product and fake_reviewer and five_star:
        return "candidate_fake"
    if not fake_product and honest_reviewer:
        return "candidate_genuine"
    return "uncertain"


def main():
    product_labels = defaultdict(Counter)

    with zipfile.ZipFile(ZIP_PATH) as archive:
        with archive.open(CSV_NAME) as file:
            reader = csv.DictReader(
                io.TextIOWrapper(file, encoding="utf-8-sig", newline="")
            )

            for row in reader:
                asin = (row["asin"] or "").strip()
                if not asin:
                    continue

                label = candidate_label(row)
                product_labels[asin][label] += 1

    products_with_fake = sum(
        counts["candidate_fake"] > 0
        for counts in product_labels.values()
    )
    products_with_genuine = sum(
        counts["candidate_genuine"] > 0
        for counts in product_labels.values()
    )
    products_with_both = sum(
        counts["candidate_fake"] > 0
        and counts["candidate_genuine"] > 0
        for counts in product_labels.values()
    )

    print("=== PRODUCT LABEL AUDIT ===")
    print(f"Total products: {len(product_labels):,}")
    print(f"Products with candidate fake: {products_with_fake:,}")
    print(f"Products with candidate genuine: {products_with_genuine:,}")
    print(f"Products with both labels: {products_with_both:,}")

    fake_counts = [
        counts["candidate_fake"]
        for counts in product_labels.values()
        if counts["candidate_fake"] > 0
    ]
    genuine_counts = [
        counts["candidate_genuine"]
        for counts in product_labels.values()
        if counts["candidate_genuine"] > 0
    ]

    print(f"Max candidate fake reviews in one product: {max(fake_counts, default=0):,}")
    print(f"Max candidate genuine reviews in one product: {max(genuine_counts, default=0):,}")


if __name__ == "__main__":
    main()
