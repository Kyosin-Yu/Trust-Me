import csv
import io
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "dataset/raw/public_reviews_dataset_cleaned.csv_.zip"
CSV_NAME = "public_reviews_dataset_cleaned.csv"


def main():
    counts = Counter()

    with zipfile.ZipFile(ZIP_PATH) as archive:
        with archive.open(CSV_NAME) as file:
            reader = csv.DictReader(
                io.TextIOWrapper(file, encoding="utf-8-sig", newline="")
            )

            for row in reader:
                fake_product = row["fake_review_product"] == "True"
                fake_reviewer = row["reviewer_classified_fake"] == "True"
                honest_reviewer = row["reviewer_classified_honest"] == "True"
                five_star = row["review_rating"] == "5"

                labeled_fake = row["reviewer_labeled_fake"] == "1.0"
                labeled_honest = row["reviewer_labeled_honest"] == "1.0"

                # Strategy A
                if fake_product and fake_reviewer and five_star:
                    counts["A_fake"] += 1
                elif not fake_product and honest_reviewer:
                    counts["A_genuine"] += 1

                # Strategy B
                if fake_product and fake_reviewer and five_star and labeled_fake:
                    counts["B_fake"] += 1
                elif not fake_product and honest_reviewer and labeled_honest:
                    counts["B_genuine"] += 1

    print("=== TRAINING LABEL STRATEGY AUDIT ===")
    for name in ["A_fake", "A_genuine", "B_fake", "B_genuine"]:
        print(f"{name}: {counts[name]:,}")

    print(f"Strategy A total: {counts['A_fake'] + counts['A_genuine']:,}")
    print(f"Strategy B total: {counts['B_fake'] + counts['B_genuine']:,}")


if __name__ == "__main__":
    main()
