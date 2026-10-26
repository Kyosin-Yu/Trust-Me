
import json
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    recall_score,
)

from review_dataset_loader import load_config, load_partition
from train_baseline import build_pipeline
from evaluate_calibration_robustness import create_verified_splits


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "runs"
    / "EXP-08_calibrated_threshold"
)

SEED = 42
N_FOLDS = 3
THRESHOLDS = [round(i / 100, 2) for i in range(30, 81, 5)]


def evaluate_threshold(y_true, probabilities, threshold):
    """Evaluate binary candidate labels at one threshold."""

    predictions = (probabilities >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    ).ravel()

    return {
        "threshold": threshold,
        "accuracy": float(
            accuracy_score(y_true, predictions)
        ),
        "macro_f1": float(
            f1_score(
                y_true,
                predictions,
                average="macro",
                zero_division=0,
            )
        ),
        "genuine_recall": float(
            recall_score(
                y_true,
                predictions,
                pos_label=0,
                zero_division=0,
            )
        ),
        "fake_recall": float(
            recall_score(
                y_true,
                predictions,
                pos_label=1,
                zero_division=0,
            )
        ),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def main():
    print("=== EXP-08: CALIBRATED THRESHOLD EVALUATION ===")

    config = load_config()

    if config["experiment_id"] != "review_tfidf_lr_v1":
        raise ValueError(
            "EXP-08 requires the standard EXP-01 configuration"
        )

    X_train, y_train, train_df = load_partition(
        "train", config
    )

    X_val, y_val, _ = load_partition(
        "validation", config
    )

    print(f"Training reviews: {len(X_train):,}")
    print(f"Validation reviews: {len(X_val):,}")
    print(f"Calibration seed: {SEED}")
    print(f"Calibration folds: {N_FOLDS}")

    # Reproduce the product-grouped EXP-06 configuration.
    splits, fold_records = create_verified_splits(
        X_train,
        y_train,
        train_df["asin"],
        SEED,
    )

    model = CalibratedClassifierCV(
        estimator=build_pipeline(config),
        method="sigmoid",
        cv=splits,
        ensemble=True,
        n_jobs=1,
    )

    print("\nFitting calibrated model...")
    model.fit(X_train, y_train)

    fake_class_index = list(model.classes_).index(1)

    probabilities = model.predict_proba(X_val)[
        :, fake_class_index
    ]

    # Threshold changes predictions, not the trained model.
    results = pd.DataFrame([
        evaluate_threshold(y_val, probabilities, threshold)
        for threshold in THRESHOLDS
    ])

    # Predefined selection rule:
    # Highest Macro-F1; for ties prefer lower threshold.
    ranked = results.sort_values(
        ["macro_f1", "threshold"],
        ascending=[False, True],
    )

    best = ranked.iloc[0]

    # Check consistency with EXP-06 at threshold 0.60.
    reference = results.loc[
        np.isclose(results["threshold"], 0.60)
    ].iloc[0]

    if not np.isclose(
        reference["macro_f1"],
        0.705708,
        atol=0.000001,
    ):
        raise ValueError(
            "EXP-06 Macro-F1 reproduction check failed"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results.to_csv(
        OUTPUT_DIR / "threshold_results.csv",
        index=False,
    )

    metadata = {
        "experiment": "EXP-08",
        "base_experiment": "EXP-01",
        "calibration_reference": "EXP-06",
        "dataset_version": config["dataset_version"],
        "calibration_method": "sigmoid",
        "calibration_seed": SEED,
        "calibration_folds": N_FOLDS,
        "grouping_variable": "asin",
        "ensemble": True,
        "thresholds": THRESHOLDS,
        "primary_selection_metric": "validation_macro_f1",
        "tie_breaking_rule": "lower_threshold",
        "evaluation_partition": "validation",
        "test_dataset_accessed": False,
    }

    with (OUTPUT_DIR / "experiment_metadata.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(metadata, file, indent=2)

    selected = {
        "experiment": "EXP-08",
        "selection_status": "provisional_validation_selection",
        "threshold": float(best["threshold"]),
        "validation_macro_f1": float(best["macro_f1"]),
        "validation_accuracy": float(best["accuracy"]),
        "genuine_recall": float(best["genuine_recall"]),
        "fake_recall": float(best["fake_recall"]),
        "calibration_seed": SEED,
        "test_dataset_accessed": False,
    }

    with (OUTPUT_DIR / "selected_threshold.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(selected, file, indent=2)

    print("\n=== THRESHOLD RESULTS ===")
    print(
        results[
            [
                "threshold",
                "accuracy",
                "macro_f1",
                "genuine_recall",
                "fake_recall",
            ]
        ].to_string(index=False)
    )

    print("\n=== BEST TESTED THRESHOLD ===")
    print(f"Threshold: {best['threshold']:.2f}")
    print(f"Macro-F1: {best['macro_f1']:.6f}")
    print(f"Accuracy: {best['accuracy']:.6f}")
    print(f"Genuine Recall: {best['genuine_recall']:.6f}")
    print(f"Fake Recall: {best['fake_recall']:.6f}")

    print("\n=== FOLD INTEGRITY ===")
    print(f"Verified folds: {len(fold_records)}")
    print(
        "Maximum product overlap:",
        max(r["product_overlap"] for r in fold_records),
    )

    print("\nResults saved to:", OUTPUT_DIR)
    print("Test dataset: NOT ACCESSED")


if __name__ == "__main__":
    main()
