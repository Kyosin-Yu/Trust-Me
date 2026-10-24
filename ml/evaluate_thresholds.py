import csv
from pathlib import Path

import numpy as np

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from review_dataset_loader import load_config, load_partition
from train_baseline import build_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "reports"
)

THRESHOLDS = [
    round(value, 2)
    for value in np.arange(0.30, 0.801, 0.05)
]


def evaluate_threshold(y_true, probabilities, threshold):
    """Evaluate classification performance at one threshold."""

    predictions = (
        probabilities >= threshold
    ).astype(int)

    scores = {
        "threshold": threshold,
        "accuracy": accuracy_score(y_true, predictions),
        "macro_f1": f1_score(
            y_true,
            predictions,
            average="macro",
            zero_division=0,
        ),
        "genuine_precision": precision_score(
            y_true,
            predictions,
            pos_label=0,
            zero_division=0,
        ),
        "genuine_recall": recall_score(
            y_true,
            predictions,
            pos_label=0,
            zero_division=0,
        ),
        "fake_precision": precision_score(
            y_true,
            predictions,
            pos_label=1,
            zero_division=0,
        ),
        "fake_recall": recall_score(
            y_true,
            predictions,
            pos_label=1,
            zero_division=0,
        ),
    }

    return scores


def main():
    # EXP-03 uses the ORIGINAL standard LR configuration.
    config = load_config()

    assert config["logistic_regression"]["class_weight"] is None, (
        "EXP-03 requires the standard EXP-01 configuration."
    )

    print("=== EXP-03: THRESHOLD ANALYSIS ===")
    print(f"Base experiment: {config['experiment_id']}")
    print("Class weighting: None")

    X_train, y_train, _ = load_partition(
        "train",
        config,
    )

    X_val, y_val, _ = load_partition(
        "validation",
        config,
    )

    model = build_pipeline(config)

    print("\nTraining EXP-01 model...")
    model.fit(X_train, y_train)
    print("Training: COMPLETED")

    # Get the probability associated with candidate class 1.
    class_index = list(
        model.named_steps["classifier"].classes_
    ).index(1)

    probabilities = model.predict_proba(
        X_val
    )[:, class_index]

    results = []

    print("\n=== VALIDATION THRESHOLD COMPARISON ===")
    print(
        "Threshold | Accuracy | Macro-F1 | "
        "Genuine Recall | Fake Recall"
    )

    for threshold in THRESHOLDS:
        metrics = evaluate_threshold(
            y_val,
            probabilities,
            threshold,
        )

        results.append(metrics)

        print(
            f"{threshold:>9.2f} | "
            f"{metrics['accuracy']:.4f}   | "
            f"{metrics['macro_f1']:.4f}   | "
            f"{metrics['genuine_recall']:.4f}         | "
            f"{metrics['fake_recall']:.4f}"
        )

    # Highest Macro-F1 wins.
    # If tied, prefer the threshold closest to 0.50.
    best = max(
        results,
        key=lambda row: (
            row["macro_f1"],
            -abs(row["threshold"] - 0.50),
        ),
    )

    best_threshold = best["threshold"]
    best_predictions = (
        probabilities >= best_threshold
    ).astype(int)

    print("\n=== BEST VALIDATION THRESHOLD ===")
    print(f"Threshold: {best_threshold:.2f}")
    print(f"Accuracy: {best['accuracy']:.4f}")
    print(f"Macro-F1: {best['macro_f1']:.4f}")
    print(
        f"Genuine recall: "
        f"{best['genuine_recall']:.4f}"
    )
    print(
        f"Fake recall: "
        f"{best['fake_recall']:.4f}"
    )

    print("\nConfusion Matrix (labels=[0, 1]):")
    print(
        confusion_matrix(
            y_val,
            best_predictions,
            labels=[0, 1],
        )
    )

    # Save experiment metrics, NOT model artifacts.
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR
        / "review_threshold_analysis_v1.csv"
    )

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "threshold",
                "accuracy",
                "macro_f1",
                "genuine_precision",
                "genuine_recall",
                "fake_precision",
                "fake_recall",
            ],
        )

        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved results: {output_path}")
    print("EXP-03: COMPLETED")
    print("Test dataset: NOT ACCESSED")


if __name__ == "__main__":
    main()
