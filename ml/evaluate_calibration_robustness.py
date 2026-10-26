import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedGroupKFold

from review_dataset_loader import load_config, load_partition
from train_baseline import build_pipeline
from evaluate_probability_calibration import (
    calculate_metrics,
    reliability_table,
    calculate_ece,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "runs"
    / "EXP-07_calibration_robustness"
)

SEEDS = [42, 123, 2026]
N_FOLDS = 3
THRESHOLD = 0.60

METRICS = [
    "brier_score",
    "log_loss",
    "ece_10_bins",
    "accuracy",
    "macro_f1",
]


def evaluate_probabilities(y_true, probabilities):
    """Use exactly the same metric definitions as EXP-06."""

    metrics = calculate_metrics(
        y_true, probabilities, threshold=THRESHOLD
    )

    reliability = reliability_table(y_true, probabilities)

    metrics["ece_10_bins"] = calculate_ece(reliability)

    return metrics


def create_verified_splits(X, y, groups, seed):
    """Create product-disjoint calibration folds."""

    cv = StratifiedGroupKFold(
        n_splits=N_FOLDS,
        shuffle=True,
        random_state=seed,
    )

    splits = list(cv.split(X, y, groups=groups))
    records = []

    for fold, (fit_idx, calibration_idx) in enumerate(
        splits, start=1
    ):
        fit_products = set(groups.iloc[fit_idx])
        calibration_products = set(
            groups.iloc[calibration_idx]
        )

        overlap = len(fit_products & calibration_products)

        fit_labels = set(y.iloc[fit_idx])
        calibration_labels = set(
            y.iloc[calibration_idx]
        )

        if overlap:
            raise ValueError(
                f"Seed {seed}, fold {fold}: product overlap"
            )

        if fit_labels != {0, 1}:
            raise ValueError(
                f"Seed {seed}, fold {fold}: fitting class missing"
            )

        if calibration_labels != {0, 1}:
            raise ValueError(
                f"Seed {seed}, fold {fold}: calibration class missing"
            )

        records.append({
            "seed": seed,
            "fold": fold,
            "fitting_reviews": len(fit_idx),
            "calibration_reviews": len(calibration_idx),
            "fitting_products": len(fit_products),
            "calibration_products": len(calibration_products),
            "product_overlap": overlap,
            "fitting_genuine": int(
                (y.iloc[fit_idx] == 0).sum()
            ),
            "fitting_fake": int(
                (y.iloc[fit_idx] == 1).sum()
            ),
            "calibration_genuine": int(
                (y.iloc[calibration_idx] == 0).sum()
            ),
            "calibration_fake": int(
                (y.iloc[calibration_idx] == 1).sum()
            ),
        })

    return splits, records


def main():
    print("=== EXP-07: CALIBRATION ROBUSTNESS ===")

    config = load_config()

    if config["experiment_id"] != "review_tfidf_lr_v1":
        raise ValueError(
            "EXP-07 requires the standard EXP-01 configuration"
        )

    X_train, y_train, train_df = load_partition(
        "train", config
    )

    X_val, y_val, _ = load_partition(
        "validation", config
    )

    groups = train_df["asin"]

    print(f"Training reviews: {len(X_train):,}")
    print(f"Validation reviews: {len(X_val):,}")
    print(f"Seeds: {SEEDS}")

    # Train the uncalibrated comparison model once.
    print("\nFitting uncalibrated baseline...")

    baseline = build_pipeline(config)
    baseline.fit(X_train, y_train)

    baseline_idx = list(baseline.classes_).index(1)
    baseline_probs = baseline.predict_proba(X_val)[
        :, baseline_idx
    ]

    baseline_metrics = evaluate_probabilities(
        y_val, baseline_probs
    )

    print(
        "Baseline ECE:",
        f"{baseline_metrics['ece_10_bins']:.6f}",
    )

    records = []
    all_fold_records = []

    for seed in SEEDS:
        print(f"\n=== SEED {seed} ===")

        splits, fold_records = create_verified_splits(
            X_train, y_train, groups, seed
        )

        all_fold_records.extend(fold_records)

        calibrated = CalibratedClassifierCV(
            estimator=build_pipeline(config),
            method="sigmoid",
            cv=splits,
            ensemble=True,
            n_jobs=1,
        )

        calibrated.fit(X_train, y_train)

        fake_idx = list(calibrated.classes_).index(1)

        probabilities = calibrated.predict_proba(X_val)[
            :, fake_idx
        ]

        metrics = evaluate_probabilities(
            y_val, probabilities
        )

        record = {
            "seed": seed,
            **metrics,
        }

        for metric in METRICS:
            record[f"{metric}_improvement"] = (
                baseline_metrics[metric] - metrics[metric]
                if metric in (
                    "brier_score",
                    "log_loss",
                    "ece_10_bins",
                )
                else metrics[metric] - baseline_metrics[metric]
            )

        records.append(record)

        print(
            f"Brier Score: {metrics['brier_score']:.6f}"
        )
        print(f"Log Loss: {metrics['log_loss']:.6f}")
        print(f"ECE: {metrics['ece_10_bins']:.6f}")
        print(f"Accuracy: {metrics['accuracy']:.6f}")
        print(f"Macro-F1: {metrics['macro_f1']:.6f}")

    results = pd.DataFrame(records)

    summary_records = []

    for metric in METRICS:
        values = results[metric]
        improvement = results[f"{metric}_improvement"]

        summary_records.append({
            "metric": metric,
            "uncalibrated_baseline": baseline_metrics[metric],
            "calibrated_mean": values.mean(),
            "calibrated_std": values.std(ddof=1),
            "calibrated_min": values.min(),
            "calibrated_max": values.max(),
            "mean_improvement": improvement.mean(),
            "seeds_improved": int((improvement > 0).sum()),
            "seeds_tested": len(SEEDS),
        })

    summary = pd.DataFrame(summary_records)
    fold_df = pd.DataFrame(all_fold_records)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results.to_csv(
        OUTPUT_DIR / "per_seed_results.csv",
        index=False,
    )

    summary.to_csv(
        OUTPUT_DIR / "robustness_summary.csv",
        index=False,
    )

    fold_df.to_csv(
        OUTPUT_DIR / "fold_verification.csv",
        index=False,
    )

    metadata = {
        "experiment": "EXP-07",
        "base_experiment": "EXP-01",
        "calibration_reference": "EXP-06",
        "dataset_version": config["dataset_version"],
        "seeds": SEEDS,
        "folds": N_FOLDS,
        "grouping_variable": "asin",
        "calibration_method": "sigmoid",
        "ensemble": True,
        "comparison_threshold": THRESHOLD,
        "evaluation_partition": "validation",
        "ece_bins": 10,
        "test_dataset_accessed": False,
    }

    with (OUTPUT_DIR / "experiment_metadata.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(metadata, file, indent=2)

    print("\n=== PER-SEED RESULTS ===")
    print(results.to_string(index=False))

    print("\n=== ROBUSTNESS SUMMARY ===")
    print(summary.to_string(index=False))

    print("\n=== FOLD INTEGRITY ===")
    print(
        f"Total folds checked: {len(fold_df)}"
    )
    print(
        "Maximum product overlap:",
        fold_df["product_overlap"].max(),
    )

    print("\nResults saved to:", OUTPUT_DIR)
    print("Test dataset: NOT ACCESSED")


if __name__ == "__main__":
    main()
