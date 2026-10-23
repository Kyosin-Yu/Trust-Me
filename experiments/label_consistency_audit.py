import csv
import io
import zipfile
from collections import Counter
from collections import defaultdict
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
    text_labels = defaultdict(set)
    text_counts = defaultdict(int)
    text_label_counts = defaultdict(Counter)

    with zipfile.ZipFile(ZIP_PATH) as archive:
        with archive.open(CSV_NAME) as file:
            reader = csv.DictReader(
                io.TextIOWrapper(file, encoding="utf-8-sig", newline="")
            )

            for row in reader:
                text = (row["review_text"] or "").strip()
                label = candidate_label(row)
                text_label_counts[text][label] += 1
                text_counts[text] += 1
                text_labels[text].add(label)

    duplicated_groups = sum(
        count > 1 for count in text_counts.values()
    )

    conflicting_groups = sum(
        "candidate_fake" in labels
        and "candidate_genuine" in labels
        for labels in text_labels.values()
    )

    conflicting_rows = sum(
        text_counts[text]
        for text, labels in text_labels.items()
        if "candidate_fake" in labels
        and "candidate_genuine" in labels
    )

    print("=== LABEL CONSISTENCY AUDIT ===")
    print(f"Duplicate text groups: {duplicated_groups:,}")
    print(f"Fake/genuine conflicting text groups: {conflicting_groups:,}")
    print(f"All rows in conflicting groups: {conflicting_rows:,}")

    conflicting_label_counts = Counter()

    for labels in text_label_counts.values():
        if labels["candidate_fake"] > 0 and labels["candidate_genuine"] > 0:
            conflicting_label_counts.update(labels)

    print("\n=== CONFLICTING GROUP LABEL COMPOSITION ===")
    for label in ["candidate_fake", "candidate_genuine", "uncertain"]:
        print(f"{label}: {conflicting_label_counts[label]:,}")

if __name__ == "__main__":
    main()
