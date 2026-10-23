import csv
import io
import random
import zipfile
import json
from datetime import datetime, timezone
from collections import Counter, defaultdict
from pathlib import Path

#Dataset Configuration
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = (
    PROJECT_ROOT
    / "dataset"
    / "raw"
    / "public_reviews_dataset_cleaned.csv_.zip"
)
CSV_NAME = "public_reviews_dataset_cleaned.csv"
RANDOM_SEED = 42

#Strategy A Label Assignment
def assign_strategy_a_label(row: dict[str, str]) -> int | None:
    """
    Assign a provisional training label.

    1 = Candidate fake review
    0 = Candidate genuine review
    None = Unknown / excluded from supervised training

    These are research-derived proxy labels,
    not independently verified fraud labels.
    """

    fake_product = row["fake_review_product"] == "True"
    fake_reviewer = row["reviewer_classified_fake"] == "True"
    honest_reviewer = row["reviewer_classified_honest"] == "True"
    five_star = row["review_rating"] == "5"

    if fake_product and fake_reviewer and five_star:
        return 1
    if not fake_product and honest_reviewer:
        return 0

    return None

#Load Candidate Reviews
def load_candidate_reviews() -> list[dict]:
    """
    Load Strategy A candidate reviews directly from the ZIP.

    The original dataset is not modified.
    """

    candidates = []
    with zipfile.ZipFile(ZIP_PATH) as archive:
        with archive.open(CSV_NAME) as file:
            reader = csv.DictReader(
                io.TextIOWrapper(
                    file,
                    encoding="utf-8-sig",
                    newline=""
                )
            )
            for row in reader:
                label = assign_strategy_a_label(row)
                if label is None:
                    continue
                candidates.append({
                    "review_id": row["review_id"],
                    "asin": row["asin"],
                    "reviewer_id": row["reviewer_id"],
                    "review_text": row["review_text"].strip(),
                    "label": label,
                })
    return candidates

#Remove Conflicting Texts
def filter_conflicting_texts(candidates: list[dict]):
    """
    Remove candidate reviews whose identical text
    appears with both candidate labels.

    Same-label duplicate texts are retained for now.
    """

    text_labels = defaultdict(set)
    for row in candidates:
        text_labels[row["review_text"]].add(row["label"])
    conflicting_texts = {
        text
        for text, labels in text_labels.items()
        if len(labels) > 1
    }
    filtered_candidates = [
        row
        for row in candidates
        if row["review_text"] not in conflicting_texts
    ]
    return filtered_candidates, conflicting_texts

#Product-Based Dataset Splitting
def split_by_product(candidates: list[dict], seed: int = 42):
    """
    Create Train, Validation, and Test partitions.

    Target distribution:
        Train      = 70%
        Validation = 15%
        Test       = 15%

    Rules:
        - All reviews from the same ASIN stay together.
        - Each class is allocated separately.
        - A fixed seed makes allocation reproducible.

    This initial split does not yet guarantee zero
    duplicate-text or reviewer overlap across partitions.
    """
    rng = random.Random(seed)

    #Group all reviews by product
    grouped = defaultdict(list)
    for row in candidates:
        grouped[row["asin"]].append(row)

    #Separate products by candidate class
    class_groups = {
        0: [],
        1: [],
    }
    for asin, reviews in grouped.items():
        labels = {
            review["label"]
            for review in reviews
        }
        assert len(labels) == 1, (
            f"Mixed labels found for product {asin}"
        )
        label = next(iter(labels))
        class_groups[label].append(
            (asin, reviews)
        )
    partitions = {
        "train": [],
        "validation": [],
        "test": [],
    }

    #Allocate fake and genuine product groups separately
    for label in (0, 1):

        #Sort before shuffling for reproducibility
        groups = sorted(
            class_groups[label],
            key=lambda item: item[0]
        )
        rng.shuffle(groups)
        total_rows = sum(
            len(reviews)
            for _, reviews in groups
        )
        targets = {
            "train": total_rows * 0.70,
            "validation": total_rows * 0.15,
            "test": total_rows * 0.15,
        }
        allocated = {
            name: 0
            for name in partitions
        }
        #Allocate larger product groups first
        #Python stable sort preserves seeded order for ties
        groups.sort(
            key=lambda item: len(item[1]),
            reverse=True
        )
        for asin, reviews in groups:
            partition_name = max(
                partitions,
                key=lambda name: (
                    targets[name] - allocated[name]
                )
            )
            partitions[partition_name].extend(reviews)
            allocated[partition_name] += len(reviews)
    return partitions


def remove_cross_partition_text_overlap(partitions):
    """
    Remove exact-text overlap across dataset partitions.

    Retention priority:
        1. Train
        2. Validation
        3. Test

    The original partition lists are not modified.
    """

    cleaned = {}
    removed = {}
    seen_texts = set()
    for name in ("train", "validation", "test"):
        kept_rows = []
        removed_rows = []
        # Texts already assigned to earlier partitions
        earlier_texts = seen_texts.copy()
        for row in partitions[name]:
            text = row["review_text"]
            if text in earlier_texts:
                removed_rows.append(row)
            else:
                kept_rows.append(row)
        cleaned[name] = kept_rows
        removed[name] = removed_rows
        # Same-partition duplicates are allowed
        seen_texts.update(
            row["review_text"] for row in kept_rows
        )
    return cleaned, removed


def verify_cleaned_partitions(cleaned_partitions):
    """Verify all final training partitions after decontamination."""
    names = ("train", "validation", "test")
    all_review_ids = set()
    product_sets = {}
    text_sets = {}
    print("\n=== FINAL DATASET VERIFICATION ===")
    for name in names:
        rows = cleaned_partitions[name]
        labels = Counter(row["label"] for row in rows)
        review_ids = {row["review_id"] for row in rows}
        assert len(rows) > 0
        assert labels[0] > 0 and labels[1] > 0
        assert len(review_ids) == len(rows)
        assert all_review_ids.isdisjoint(review_ids)
        all_review_ids.update(review_ids)
        product_sets[name] = {row["asin"] for row in rows}
        text_sets[name] = {row["review_text"] for row in rows}
        print(
            f"{name}: {len(rows):,} reviews | "
            f"products={len(product_sets[name]):,} | "
            f"fake={labels[1]:,} | genuine={labels[0]:,}"
        )
    for i, first in enumerate(names):
        for second in names[i + 1:]:
            assert product_sets[first].isdisjoint(
                product_sets[second]
            ), f"Product overlap: {first} vs {second}"
            assert text_sets[first].isdisjoint(
                text_sets[second]
            ), f"Text overlap: {first} vs {second}"
    assert len(all_review_ids) == 66_428

    print("Final product isolation: PASSED")
    print("Final exact-text isolation: PASSED")
    print("Final review ID uniqueness: PASSED")
    print("Final class coverage: PASSED")


def export_cleaned_dataset(cleaned_partitions, removed_rows):
    """Export verified partitions and reproducibility metadata."""
    output_dir = (
        PROJECT_ROOT
        / "dataset"
        / "processed"
        / "strategy_a_v1"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    columns = [
        "review_id",
        "asin",
        "reviewer_id",
        "review_text",
        "label",
    ]
    partition_summary = {}
    for name in ("train", "validation", "test"):
        rows = cleaned_partitions[name]
        output_path = output_dir / f"{name}.csv"
        with output_path.open(
            "w", encoding="utf-8", newline=""
        ) as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        labels = Counter(row["label"] for row in rows)
        partition_summary[name] = {
            "reviews": len(rows),
            "candidate_fake": labels[1],
            "candidate_genuine": labels[0],
            "unique_products": len({
                row["asin"] for row in rows
            }),
        }
        print(f"Exported: {output_path}")

    # Preserve an audit trail of text-overlap exclusions
    excluded_path = output_dir / "excluded_text_overlap.csv"
    with excluded_path.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "original_partition",
                "review_id",
                "asin",
                "label",
                "reason",
            ],
        )
        writer.writeheader()
        for name in ("train", "validation", "test"):
            for row in removed_rows[name]:
                writer.writerow({
                    "original_partition": name,
                    "review_id": row["review_id"],
                    "asin": row["asin"],
                    "label": row["label"],
                    "reason": "cross_partition_exact_text",
                })
    manifest = {
        "dataset_name": "Amazon research review dataset",
        "strategy": "A",
        "version": "1.0",
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "random_seed": RANDOM_SEED,
        "label_meaning": {
            "1": "candidate_fake_proxy",
            "0": "candidate_genuine_proxy",
        },
        "splitting_method": "product_grouped_class_aware",
        "target_proportions": {
            "train": 0.70,
            "validation": 0.15,
            "test": 0.15,
        },
        "decontamination": {
            "method": "exact_stripped_text",
            "retention_priority": [
                "train", "validation", "test"
            ],
            "candidate_reviews_before": 66521,
            "excluded_reviews": sum(
                len(rows) for rows in removed_rows.values()
            ),
            "candidate_reviews_after": sum(
                len(rows)
                for rows in cleaned_partitions.values()
            ),
        },
        "partitions": partition_summary,
        "limitations": [
            "Labels are research-derived proxies, not verified fraud ground truth.",
            "Product and exact-text isolation are enforced across partitions.",
            "Reviewer overlap remains and must be disclosed.",
            "Cross-platform generalization has not been established.",
            "TF-IDF vocabulary and model parameters must be fitted on training data only.",
        ],
    }
    manifest_path = output_dir / "split_manifest.json"
    with manifest_path.open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(manifest, file, indent=2, ensure_ascii=False)
    print(f"Exported: {excluded_path}")
    print(f"Exported: {manifest_path}")
    print("Dataset export: COMPLETED")


def main():
#Load strategy A candidate reviews
    candidates = load_candidate_reviews()
    labels = Counter(
        row["label"]
        for row in candidates
    )
    unique_products = {
        row["asin"]
        for row in candidates
    }
    unique_reviewers = {
        row["reviewer_id"]
        for row in candidates
    }
    print("\n=== STRATEGY A CANDIDATE DATASET ===")
    print(f"Total candidates: {len(candidates):,}")
    print(f"Candidate fake (1): {labels[1]:,}")
    print(f"Candidate genuine (0): {labels[0]:,}")
    print(f"Unique products: {len(unique_products):,}")
    print(f"Unique reviewers: {len(unique_reviewers):,}")
    assert len(candidates) == 67_222
    assert labels[1] == 52_209
    assert labels[0] == 15_013
    print("Candidate count verification: PASSED")

#Filter conflicting texts
    filtered_candidates, conflicting_texts = (
        filter_conflicting_texts(candidates)
    )
    filtered_labels = Counter(
        row["label"]
        for row in filtered_candidates
    )
    print("\n=== CONFLICTING TEXT FILTER ===")
    print(
        f"Conflicting text groups: "
        f"{len(conflicting_texts):,}"
    )
    print(
        f"Excluded candidate reviews: "
        f"{len(candidates) - len(filtered_candidates):,}"
    )
    print(
        f"Remaining candidate reviews: "
        f"{len(filtered_candidates):,}"
    )
    print(
        f"Remaining fake candidates: "
        f"{filtered_labels[1]:,}"
    )
    print(
        f"Remaining genuine candidates: "
        f"{filtered_labels[0]:,}"
    )
    assert len(conflicting_texts) == 89
    assert len(filtered_candidates) == 66_521
    assert filtered_labels[1] == 52_045
    assert filtered_labels[0] == 14_476
    print("Conflicting text filter verification: PASSED")

    # Product group audit
    product_labels = {}
    for row in filtered_candidates:
        asin = row["asin"]
        label = row["label"]
        if asin in product_labels:
            assert product_labels[asin] == label, (
                f"Conflicting labels within product {asin}"
            )
        else:
            product_labels[asin] = label
    product_counts = Counter(
        product_labels.values()
    )
    print("\n=== FILTERED PRODUCT GROUP AUDIT ===")
    print(
        f"Total product groups: "
        f"{len(product_labels):,}"
    )
    print(
        f"Fake-candidate product groups: "
        f"{product_counts[1]:,}"
    )
    print(
        f"Genuine-candidate product groups: "
        f"{product_counts[0]:,}"
    )
    assert len(product_labels) == 2_942
    assert product_counts[1] == 1_402
    assert product_counts[0] == 1_540
    print("Within-product label consistency: PASSED")

    #Product-grouped dataset split
    partitions = split_by_product(
        filtered_candidates,
        seed=RANDOM_SEED
    )
    print("\n=== PRODUCT-GROUPED SPLIT ===")
    product_sets = {}
    all_partition_review_ids = set()
    for name, rows in partitions.items():
        partition_labels = Counter(
            row["label"]
            for row in rows
        )
        partition_products = {
            row["asin"]
            for row in rows
        }
        product_sets[name] = partition_products
        percentage = (
            len(rows) / len(filtered_candidates)
        ) * 100
        print(
            f"{name}: "
            f"{len(rows):,} reviews "
            f"({percentage:.2f}%) | "
            f"fake={partition_labels[1]:,} | "
            f"genuine={partition_labels[0]:,} | "
            f"products={len(partition_products):,}"
        )

        #Every partition must contain both candidate classes
        assert partition_labels[0] > 0, (
            f"No genuine candidates in {name}"
        )
        assert partition_labels[1] > 0, (
            f"No fake candidates in {name}"
        )

        #Verify review IDs do not repeat across partitions
        review_ids = {
            row["review_id"]
            for row in rows
        }
        assert len(review_ids) == len(rows), (
            f"Duplicate review IDs detected in {name}"
        )
        assert all_partition_review_ids.isdisjoint(
            review_ids
        ), (
            f"Review ID leakage detected in {name}"
        )
        all_partition_review_ids.update(review_ids)

    #Check no product appears in multiple partitions
    assert product_sets["train"].isdisjoint(
        product_sets["validation"]
    )
    assert product_sets["train"].isdisjoint(
        product_sets["test"]
    )
    assert product_sets["validation"].isdisjoint(
        product_sets["test"]
    )

    #Verify no candidate was lost during splitting
    assert sum(
        len(rows)
        for rows in partitions.values()
    ) == 66_521
    assert len(all_partition_review_ids) == 66_521
    assert len(
        set().union(*product_sets.values())
    ) == 2_942

    print(
        "Product isolation, review ID uniqueness, "
        "class coverage and total count: PASSED"
    )

    #Cross partition leakage audit
    print("\n=== CROSS-PARTITION LEAKAGE AUDIT ===")

    #Collect unique review texts in each partition
    text_sets = {
        name: {
            row["review_text"]
            for row in rows
        }
        for name, rows in partitions.items()
    }

    #Collect valid reviewer IDs in each partition
    #Empty reviewer IDs are excluded from this comparison
    reviewer_sets = {
        name: {
            row["reviewer_id"]
            for row in rows
            if row["reviewer_id"].strip()
        }
        for name, rows in partitions.items()
    }

    partition_pairs = [
        ("train", "validation"),
        ("train", "test"),
        ("validation", "test"),
    ]

    print("Duplicate text overlap:")

    for first, second in partition_pairs:
        shared_texts = text_sets[first] & text_sets[second]

        print(
            f"{first} vs {second}: "
            f"{len(shared_texts):,} shared unique texts"
        )

    print("\nReviewer ID overlap:")

    for first, second in partition_pairs:
        shared_reviewers = (
            reviewer_sets[first] & reviewer_sets[second]
        )

        print(
            f"{first} vs {second}: "
            f"{len(shared_reviewers):,} shared reviewers"
        )

    print("\nLeakage audit: COMPLETED")
    print("Any detected overlap requires evaluation.")

    #Measure affected review rows
    print("\n=== CROSS-PARTITION AFFECTED ROWS ===")
    for name, rows in partitions.items():
        other_names = [
            other
            for other in partitions
            if other != name
        ]
        # Text appearing in at least one other partition
        other_texts = set().union(
            *(text_sets[other] for other in other_names)
        )
        #Reviewer IDs appearing in at least one other partition
        other_reviewers = set().union(
            *(reviewer_sets[other] for other in other_names)
        )
        affected_text_rows = sum(
            row["review_text"] in other_texts
            for row in rows
        )
        affected_reviewer_rows = sum(
            bool(row["reviewer_id"].strip())
            and row["reviewer_id"] in other_reviewers
            for row in rows
        )
        text_percentage = (
            affected_text_rows / len(rows) * 100
        )
        reviewer_percentage = (
            affected_reviewer_rows / len(rows) * 100
        )
        print(f"\n{name.upper()}")
        print(
            f"Reviews affected by cross-partition text: "
            f"{affected_text_rows:,} ({text_percentage:.2f}%)"
        )
        print(
            f"Reviews affected by cross-partition reviewer IDs: "
            f"{affected_reviewer_rows:,} ({reviewer_percentage:.2f}%)"
        )
    print("\nAffected-row audit: COMPLETED")
    
    # Exact-text decontamination
    cleaned_partitions, removed_rows = (
        remove_cross_partition_text_overlap(partitions)
    )
    print("\n=== EXACT-TEXT DECONTAMINATION ===")
    for name in ("train", "validation", "test"):
        original_count = len(partitions[name])
        cleaned_count = len(cleaned_partitions[name])
        removed_count = len(removed_rows[name])

        labels = Counter(
            row["label"]
            for row in cleaned_partitions[name]
        )

        print(
            f"{name}: "
            f"before={original_count:,} | "
            f"after={cleaned_count:,} | "
            f"removed={removed_count:,} | "
            f"fake={labels[1]:,} | "
            f"genuine={labels[0]:,}"
        )
        assert cleaned_count + removed_count == original_count
        assert labels[0] > 0 and labels[1] > 0

    # Verify exact-text isolation after filtering
    final_text_sets = {
        name: {
            row["review_text"]
            for row in rows
        }
        for name, rows in cleaned_partitions.items()
    }
    assert final_text_sets["train"].isdisjoint(
        final_text_sets["validation"]
    )
    assert final_text_sets["train"].isdisjoint(
        final_text_sets["test"]
    )
    assert final_text_sets["validation"].isdisjoint(
        final_text_sets["test"]
    )
    total_removed = sum(
        len(rows) for rows in removed_rows.values()
    )
    total_remaining = sum(
        len(rows) for rows in cleaned_partitions.values()
    )
    assert total_remaining + total_removed == 66_521
    print(f"\nTotal removed: {total_removed:,}")
    print(f"Final candidate reviews: {total_remaining:,}")
    print("Cross-partition exact-text overlap: ZERO")
    print("Exact-text decontamination: PASSED")

    verify_cleaned_partitions(cleaned_partitions)
    print("\n=== DATASET EXPORT ===")
    export_cleaned_dataset(cleaned_partitions,removed_rows,)

    print("\n=== CURRENT STATUS ===")
    print("Candidate selection: PASSED")
    print("Conflicting text filtering: PASSED")
    print("Product group audit: PASSED")
    print("Initial product-grouped split: PASSED")
    print("Cross-partition text/reviewer audit: COMPLETED")
    print("Dataset export: COMPLETED")
    print("Exact-text decontamination: COMPLETED")

#entry point
if __name__ == "__main__":
    main()
