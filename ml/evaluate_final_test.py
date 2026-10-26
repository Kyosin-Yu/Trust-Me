import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    brier_score_loss,
)

from review_dataset_loader import load_config, load_partition
from train_baseline import build_pipeline
from evaluate_calibration_robustness import create_verified_splits
from evaluate_probability_calibration import (
    reliability_table,
    calculate_ece,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

FROZEN_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "model_selection"
    / "frozen_model_config.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "final_evaluation"
)


def read_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def verify_frozen_configuration(frozen, baseline):
    """Fail before test access if configurations disagree."""

    if frozen["selection_status"] != "frozen_before_test_evaluation":
        raise ValueError("Model selection has not been frozen.")

    if frozen["dataset_version"] != baseline["dataset_version"]:
        raise ValueError("Dataset version mismatch.")

    if baseline["experiment_id"] != "review_tfidf_lr_v1":
        raise ValueError("Unexpected baseline experiment.")

    tfidf = baseline["tfidf"]
    lr = baseline["logistic_regression"]
    model = frozen["model"]
    calibration = frozen["calibration"]
    classification = frozen["classification"]

    expected_model = {
        "feature_extractor": "TfidfVectorizer",
        "ngram_range": tfidf["ngram_range"],
        "max_features": tfidf["max_features"],
        "min_df": tfidf["min_df"],
        "lowercase": tfidf["lowercase"],
        "sublinear_tf": tfidf["sublinear_tf"],
        "norm": tfidf["norm"],
        "classifier": "LogisticRegression",
        "C": lr["C"],
        "class_weight": lr["class_weight"],
        "max_iter": lr["max_iter"],
        "random_state": lr["random_state"],
    }

    if model != expected_model:
        raise ValueError(
            "Frozen model parameters do not match the "
            "baseline configuration."
        )

    expected_calibration = {
        "method": "sigmoid",
        "cv_strategy": "StratifiedGroupKFold",
        "n_splits": 3,
        "shuffle": True,
        "random_state": 42,
        "group_column": "asin",
        "ensemble": True,
    }

    if calibration != expected_calibration:
        raise ValueError("Unexpected calibration configuration.")

    if classification["positive_class"] != 1:
        raise ValueError("Unexpected positive class.")

    if classification["negative_class"] != 0:
        raise ValueError("Unexpected negative class.")

    if classification["threshold"] != 0.65:
        raise ValueError("Frozen threshold differs from EXP-08.")

    if classification["selection_metric"] != "validation_macro_f1":
        raise ValueError("Unexpected selection metric.")

    if (
        classification["selection_rule"]
        != "highest_macro_f1_tie_lower_threshold"
    ):
        raise ValueError("Unexpected threshold selection rule.")

    policy = frozen["evaluation_policy"]

    if policy["test_dataset_accessed_during_selection"] is not False:
        raise ValueError("Test access policy violation.")

    if policy["allow_test_based_tuning"] is not False:
        raise ValueError("Test-based tuning is not permitted.")

    # Verify baseline metadata and the actual sklearn estimator.
    pipeline = build_pipeline(baseline)

    actual_tfidf = pipeline.named_steps["tfidf"].get_params()
    actual_lr = pipeline.named_steps["classifier"].get_params()

    for name in (
        "ngram_range",
        "max_features",
        "min_df",
        "lowercase",
        "sublinear_tf",
        "norm",
    ):
        actual = actual_tfidf[name]
        expected = model[name]

        if name == "ngram_range":
            expected = tuple(expected)

        if actual != expected:
            raise ValueError(f"TF-IDF parameter mismatch: {name}")

    for name in ("C", "class_weight", "max_iter", "random_state"):
        if actual_lr[name] != model[name]:
            raise ValueError(f"Classifier parameter mismatch: {name}")

    return True



def verify_no_overlap(train_df, validation_df, test_df, input_column):
    """
    Enforce the original DEV-03 isolation rules.

    Product, review-ID, and exact-stripped-text overlaps are
    blocking violations.

    Additional casefolded-text overlaps are reported as known
    residual limitations without modifying the dataset.
    """

    partitions = {
        "train": train_df,
        "validation": validation_df,
        "test": test_df,
    }

    def values(frame, column):
        return set(frame[column].astype(str))

    def exact_texts(frame):
        return set(
            frame[input_column]
            .astype(str)
            .str.strip()
        )

    def casefolded_texts(frame):
        return set(
            frame[input_column]
            .astype(str)
            .str.strip()
            .str.casefold()
        )

    audit_records = []

    for left_name, right_name in [
        ("train", "test"),
        ("validation", "test"),
    ]:
        left = partitions[left_name]
        right = partitions[right_name]

        product_overlap = len(
            values(left, "asin") & values(right, "asin")
        )
        review_id_overlap = len(
            values(left, "review_id") & values(right, "review_id")
        )
        exact_overlap = len(
            exact_texts(left) & exact_texts(right)
        )

        normalized_overlap_values = (
            casefolded_texts(left) & casefolded_texts(right)
        )

        normalized_overlap = len(normalized_overlap_values)

        affected_test_rows = int(
            right[input_column]
            .astype(str)
            .str.strip()
            .str.casefold()
            .isin(normalized_overlap_values)
            .sum()
        )

        record = {
            "partition_pair": f"{left_name}/{right_name}",
            "product_overlap": product_overlap,
            "review_id_overlap": review_id_overlap,
            "exact_stripped_text_overlap": exact_overlap,
            "casefolded_unique_text_overlap": normalized_overlap,
            "affected_test_rows": affected_test_rows,
        }

        audit_records.append(record)

        print(f"\n{record['partition_pair']} integrity:")
        print(f"  Product overlap: {product_overlap}")
        print(f"  Review ID overlap: {review_id_overlap}")
        print(f"  Exact-stripped-text overlap: {exact_overlap}")
        print(f"  Casefolded unique-text overlap: {normalized_overlap}")
        print(f"  Affected test rows: {affected_test_rows}")

        if product_overlap or review_id_overlap or exact_overlap:
            raise ValueError(
                f"Original DEV-03 isolation violation: "
                f"{left_name}/{right_name}"
            )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with (OUTPUT_DIR / "dataset_integrity_audit.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(
            {
                "dataset_version": "strategy_a_v1",
                "original_deduplication": "exact_stripped_text",
                "casefolded_overlap_policy": (
                    "document_and_retain_original_dataset"
                ),
                "test_records_modified": False,
                "partition_comparisons": audit_records,
                "limitation": (
                    "Case-insensitive duplicate review texts remain "
                    "across product-disjoint partitions. TF-IDF "
                    "lowercase preprocessing may make these texts "
                    "equivalent model inputs."
                ),
            },
            file,
            indent=2,
        )

    print("\nOriginal DEV-03 isolation rules: PASSED")
    print("Residual casefolded overlap: DOCUMENTED")
    return audit_records



def run_final_evaluation(frozen, baseline):
    print("\n=== FINAL HELD-OUT TEST EVALUATION ===")

    X_train, y_train, train_df = load_partition("train", baseline)
    _, _, validation_df = load_partition("validation", baseline)

    # The only intentional test-partition access.
    X_test, y_test, test_df = load_partition(
        "test",
        baseline,
        allow_test=True,
    )

    print(f"Training reviews: {len(X_train):,}")
    print(f"Test reviews: {len(X_test):,}")

    verify_no_overlap(
        train_df,
        validation_df,
        test_df,
        baseline["input_column"],
    )

    calibration = frozen["calibration"]
    threshold = frozen["classification"]["threshold"]

    splits, fold_records = create_verified_splits(
        X_train,
        y_train,
        train_df[calibration["group_column"]],
        calibration["random_state"],
    )

    if len(splits) != calibration["n_splits"]:
        raise ValueError("Calibration fold count mismatch.")

    if any(record["product_overlap"] != 0 for record in fold_records):
        raise ValueError("Calibration product leakage detected.")

    model = CalibratedClassifierCV(
        estimator=build_pipeline(baseline),
        method=calibration["method"],
        cv=splits,
        ensemble=calibration["ensemble"],
        n_jobs=1,
    )

    print("\nFitting the frozen calibrated classifier...")
    model.fit(X_train, y_train)

    positive_index = list(model.classes_).index(
        frozen["classification"]["positive_class"]
    )

    probabilities = model.predict_proba(X_test)[:, positive_index]

    predictions = (probabilities >= threshold).astype(int)

    accuracy = float(accuracy_score(y_test, predictions))
    macro_f1 = float(
        f1_score(y_test, predictions, average="macro", zero_division=0)
    )

    report = classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["candidate_genuine", "candidate_fake"],
        output_dict=True,
        zero_division=0,
    )

    matrix = confusion_matrix(y_test, predictions, labels=[0, 1])
    bins = reliability_table(y_test, probabilities)

    metrics = {
        "experiment": "final_held_out_test_v1",
        "selection_id": frozen["selection_id"],
        "dataset_version": frozen["dataset_version"],
        "partition": "test",
        "test_reviews": len(X_test),
        "threshold": threshold,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "candidate_genuine_precision": float(
            report["candidate_genuine"]["precision"]
        ),
        "candidate_genuine_recall": float(
            report["candidate_genuine"]["recall"]
        ),
        "candidate_genuine_f1": float(
            report["candidate_genuine"]["f1-score"]
        ),
        "candidate_fake_precision": float(
            report["candidate_fake"]["precision"]
        ),
        "candidate_fake_recall": float(
            report["candidate_fake"]["recall"]
        ),
        "candidate_fake_f1": float(
            report["candidate_fake"]["f1-score"]
        ),
        "brier_score": float(
            brier_score_loss(y_test, probabilities)
        ),
        "log_loss": float(
            log_loss(y_test, probabilities, labels=[0, 1])
        ),
        "ece_10_bins": float(calculate_ece(bins)),
        "confusion_matrix": matrix.tolist(),
        "test_based_tuning_performed": False,
        "label_interpretation": "research_derived_candidate_labels",
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with (OUTPUT_DIR / "final_test_metrics.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(metrics, file, indent=2)

    bins.to_csv(
        OUTPUT_DIR / "final_test_reliability_bins.csv",
        index=False,
    )

    print("\n=== FINAL TEST RESULTS ===")
    print(f"Threshold: {threshold:.2f}")
    print(f"Accuracy: {accuracy:.6f}")
    print(f"Macro-F1: {macro_f1:.6f}")
    print(f"Brier Score: {metrics['brier_score']:.6f}")
    print(f"Log Loss: {metrics['log_loss']:.6f}")
    print(f"ECE (10 bins): {metrics['ece_10_bins']:.6f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=[0, 1],
            target_names=["candidate_genuine", "candidate_fake"],
            digits=4,
            zero_division=0,
        )
    )

    print("Confusion Matrix:")
    print(matrix)
    print("\nFinal results saved to:", OUTPUT_DIR)
    print("No test-based tuning performed.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Explicitly authorize the final held-out test evaluation.",
    )
    args = parser.parse_args()

    frozen = read_json(FROZEN_PATH)
    baseline = load_config()

    verify_frozen_configuration(frozen, baseline)

    print("=== FINAL MODEL CONFIGURATION PREFLIGHT ===")
    print("Frozen configuration: VERIFIED")
    print("Baseline sklearn pipeline: VERIFIED")
    print(
        "Selected threshold:",
        frozen["classification"]["threshold"],
    )

    if not args.evaluate:
        print("Test dataset: NOT ACCESSED")
        print("Preflight: PASSED")
        return

    run_final_evaluation(frozen, baseline)


if __name__ == "__main__":
    main()
