import json
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    log_loss,
)
from sklearn.model_selection import StratifiedGroupKFold

from review_dataset_loader import load_config, load_partition
from train_baseline import build_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "runs"
    / "EXP-06_probability_calibration"
)

SEED = 42
N_FOLDS = 3
N_BINS = 10


def calculate_metrics(y_true, probabilities, threshold):
    predictions = (probabilities >= threshold).astype(int)

    return {
        "brier_score": float(
            brier_score_loss(y_true, probabilities)
        ),
        "log_loss": float(
            log_loss(y_true, probabilities, labels=[0, 1])
        ),
        "accuracy": float(
            accuracy_score(y_true, predictions)
        ),
        "macro_f1": float(
            f1_score(y_true, predictions, average="macro")
        ),
        "threshold": threshold,
    }


def reliability_table(y_true, probabilities):
    frame = pd.DataFrame({
        "actual_label": np.asarray(y_true),
        "predicted_probability": probabilities,
    })

    frame["bin"] = pd.cut(
        frame["predicted_probability"],
        bins=np.linspace(0, 1, N_BINS + 1),
        include_lowest=True,
    )

    summary = (
        frame.groupby("bin", observed=False)
        .agg(
            reviews=("actual_label", "size"),
            mean_predicted_probability=(
                "predicted_probability", "mean"
            ),
            observed_candidate_fake_rate=(
                "actual_label", "mean"
            ),
        )
        .reset_index()
    )

    summary["absolute_gap"] = (
        summary["mean_predicted_probability"]
        - summary["observed_candidate_fake_rate"]
    ).abs()

    return summary

def calculate_ece(reliability_df):
    """Calculate sample-weighted Expected Calibration Error."""

    total_reviews = reliability_df["reviews"].sum()

    if total_reviews == 0:
        raise ValueError("Cannot calculate ECE with zero reviews")

    weighted_gaps = (
        reliability_df["reviews"]
        * reliability_df["absolute_gap"].fillna(0)
    )

    return float(weighted_gaps.sum() / total_reviews)

def main():
    print("=== EXP-06: PROBABILITY CALIBRATION ===")

    config = load_config()

    if config["experiment_id"] != "review_tfidf_lr_v1":
        raise ValueError(
            "EXP-06 requires the standard EXP-01 configuration"
        )

    X_train, y_train, train_df = load_partition(
        "train", config
    )

    X_val, y_val, _ = load_partition(
        "validation", config
    )

    print(f"Training reviews: {len(X_train):,}")
    print(f"Validation reviews: {len(X_val):,}")

    # Baseline: standard uncalibrated model
    print("\nFitting uncalibrated baseline...")

    baseline = build_pipeline(config)
    baseline.fit(X_train, y_train)

    baseline_classes = baseline.classes_.tolist()
    baseline_fake_index = baseline_classes.index(1)

    baseline_probs = baseline.predict_proba(X_val)[
        :, baseline_fake_index
    ]

    # Product-disjoint folds for calibration
    cv = StratifiedGroupKFold(
        n_splits=N_FOLDS,
        shuffle=True,
        random_state=SEED,
    )

    splits = list(
        cv.split(
            X_train,
            y_train,
            groups=train_df["asin"],
        )
    )

    fold_records = []

    for number, (fit_idx, cal_idx) in enumerate(
        splits, start=1
    ):
        fit_products = set(
            train_df.iloc[fit_idx]["asin"]
        )
        cal_products = set(
            train_df.iloc[cal_idx]["asin"]
        )

        overlap = len(fit_products & cal_products)

        fitting_labels = set(y_train.iloc[fit_idx])
        calibration_labels = set(y_train.iloc[cal_idx])

        if overlap != 0:
            raise ValueError(
                f"Fold {number} has overlapping products"
            )

        if fitting_labels != {0, 1}:
            raise ValueError(
                f"Fold {number} fitting set is missing a class"
            )

        if calibration_labels != {0, 1}:
            raise ValueError(
                f"Fold {number} calibration set is missing a class"
            )

        fold_records.append({
            "fold": number,
            "fitting_reviews": len(fit_idx),
            "calibration_reviews": len(cal_idx),
            "product_overlap": overlap,
        })

    # CalibratedClassifierCV uses the precomputed
    # product-disjoint splits. It receives training
    # data only; validation is never used for fitting.
    print("\nFitting sigmoid-calibrated model...")

    calibrated = CalibratedClassifierCV(
        estimator=build_pipeline(config),
        method="sigmoid",
        cv=splits,
        ensemble=True,
        n_jobs=1,
    )

    calibrated.fit(X_train, y_train)

    calibrated_classes = calibrated.classes_.tolist()
    calibrated_fake_index = calibrated_classes.index(1)

    calibrated_probs = calibrated.predict_proba(X_val)[
        :, calibrated_fake_index
    ]

    # Compare probability quality independently
    # from threshold-based classification.
    baseline_metrics = calculate_metrics(
        y_val, baseline_probs, threshold=0.60
    )

    calibrated_metrics = calculate_metrics(
        y_val, calibrated_probs, threshold=0.60
    )

    comparison = pd.DataFrame([
        {"model": "uncalibrated", **baseline_metrics},
        {"model": "sigmoid_calibrated", **calibrated_metrics},
    ])

    uncalibrated_reliability = reliability_table(
        y_val, baseline_probs
    )

    calibrated_reliability = reliability_table(
        y_val, calibrated_probs
    )

    baseline_ece = calculate_ece(uncalibrated_reliability)
    calibrated_ece = calculate_ece(calibrated_reliability)

    comparison["ece_10_bins"] = [
        baseline_ece,
        calibrated_ece,
    ]

    uncalibrated_reliability.insert(
        0, "model", "uncalibrated"
    )

    calibrated_reliability.insert(
        0, "model", "sigmoid_calibrated"
    )

    reliability = pd.concat(
        [uncalibrated_reliability, calibrated_reliability],
        ignore_index=True,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    comparison.to_csv(
        OUTPUT_DIR / "calibration_comparison.csv",
        index=False,
    )

    reliability.to_csv(
        OUTPUT_DIR / "reliability_bins.csv",
        index=False,
    )

    pd.DataFrame(fold_records).to_csv(
        OUTPUT_DIR / "fold_verification.csv",
        index=False,
    )

    metadata = {
        "experiment": "EXP-06",
        "base_experiment": "EXP-01",
        "dataset_version": config["dataset_version"],
        "calibration_method": "sigmoid",
        "fold_strategy": "StratifiedGroupKFold",
        "grouping_column": "asin",
        "folds": N_FOLDS,
        "random_seed": SEED,
        "ensemble": True,
        "evaluation_partition": "validation",
        "classification_threshold": 0.60,
        "probability_metrics": [
            "brier_score",
            "log_loss",
        ],
        "test_dataset_accessed": False,
    }

    with (OUTPUT_DIR / "experiment_metadata.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(metadata, file, indent=2)

    print("\n=== CALIBRATION COMPARISON ===")
    print(comparison.to_string(index=False))

    print("\n=== FOLD VERIFICATION ===")
    print(
        pd.DataFrame(fold_records).to_string(index=False)
    )

    print("\nResults saved to:", OUTPUT_DIR)
    print("Test dataset: NOT ACCESSED")


if __name__ == "__main__":
    main()
