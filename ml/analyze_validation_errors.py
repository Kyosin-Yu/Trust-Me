import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
)

from review_dataset_loader import load_config, load_partition
from train_baseline import build_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "runs"
    / "EXP-05_error_analysis"
)

LENGTH_BINS = [0, 10, 30, 60, 120, float("inf")]
LENGTH_LABELS = [
    "1-10 words",
    "11-30 words",
    "31-60 words",
    "61-120 words",
    "121+ words",
]

SCORE_BINS = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
SCORE_LABELS = [
    "0.00-0.20",
    "0.20-0.40",
    "0.40-0.60",
    "0.60-0.80",
    "0.80-1.00",
]


def summarize_by_group(df, group_column):
    """Count candidate-label disagreements within each group."""

    summary = (
        df.groupby(group_column, observed=False)
        .agg(
            reviews=("actual_label", "size"),
            disagreements=("is_disagreement", "sum"),
            mean_fake_score=("fake_score", "mean"),
        )
        .reset_index()
    )

    summary["disagreement_rate"] = (
        summary["disagreements"] / summary["reviews"]
    )

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="EXP-05 validation error analysis"
    )

    parser.add_argument(
        "--config",
        default=None,
        help="Path to EXP-01 Logistic Regression config",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.60,
        help="Previously selected EXP-03 decision threshold",
    )

    args = parser.parse_args()

    if not 0.0 < args.threshold < 1.0:
        raise ValueError("Threshold must be between 0 and 1")

    config = load_config(args.config)

    if config["experiment_id"] != "review_tfidf_lr_v1":
        raise ValueError(
            "EXP-05 must use the standard EXP-01 "
            "Logistic Regression configuration"
        )

    print("=== EXP-05: VALIDATION ERROR ANALYSIS ===")
    print(f"Base model: {config['experiment_id']}")
    print(f"Threshold: {args.threshold:.2f}")

    X_train, y_train, _ = load_partition("train", config)
    X_val, y_val, val_df = load_partition("validation", config)

    model = build_pipeline(config)

    print("\nFitting baseline model...")
    model.fit(X_train, y_train)

    class_labels = list(model.named_steps["classifier"].classes_)
    fake_class_index = class_labels.index(1)

    fake_scores = model.predict_proba(X_val)[:, fake_class_index]
    predictions = (fake_scores >= args.threshold).astype(int)

    results = pd.DataFrame({
        "actual_label": y_val.to_numpy(),
        "predicted_label": predictions,
        "fake_score": fake_scores,
        "word_count": X_val.str.split().str.len().to_numpy(),
    })

    results["is_disagreement"] = (
        results["actual_label"] != results["predicted_label"]
    )

    conditions = [
        (results["actual_label"] == 0)
        & (results["predicted_label"] == 0),

        (results["actual_label"] == 0)
        & (results["predicted_label"] == 1),

        (results["actual_label"] == 1)
        & (results["predicted_label"] == 0),

        (results["actual_label"] == 1)
        & (results["predicted_label"] == 1),
    ]

    results["outcome"] = np.select(
        conditions,
        ["TN", "FP", "FN", "TP"],
        default="UNKNOWN",
    )

    results["length_group"] = pd.cut(
        results["word_count"],
        bins=LENGTH_BINS,
        labels=LENGTH_LABELS,
        include_lowest=True,
    )

    results["score_group"] = pd.cut(
        results["fake_score"],
        bins=SCORE_BINS,
        labels=SCORE_LABELS,
        include_lowest=True,
    )

    matrix = confusion_matrix(
        results["actual_label"],
        results["predicted_label"],
        labels=[0, 1],
    )

    tn, fp, fn, tp = matrix.ravel()

    metrics = {
        "experiment": "EXP-05",
        "base_experiment": "EXP-01",
        "threshold_source": "EXP-03",
        "dataset_version": config["dataset_version"],
        "evaluation_partition": "validation",
        "threshold": args.threshold,
        "validation_reviews": int(len(results)),
        "accuracy": float(
            accuracy_score(y_val, predictions)
        ),
        "macro_f1": float(
            f1_score(y_val, predictions, average="macro")
        ),
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
        "total_disagreements": int(
            results["is_disagreement"].sum()
        ),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with (OUTPUT_DIR / "metrics.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(metrics, file, indent=2)

    length_summary = summarize_by_group(
        results, "length_group"
    )

    length_summary.to_csv(
        OUTPUT_DIR / "length_analysis.csv",
        index=False,
    )

    score_summary = summarize_by_group(
        results, "score_group"
    )

    score_summary.to_csv(
        OUTPUT_DIR / "score_analysis.csv",
        index=False,
    )

    outcome_summary = (
        results.groupby("outcome")
        .agg(
            reviews=("actual_label", "size"),
            mean_word_count=("word_count", "mean"),
            mean_fake_score=("fake_score", "mean"),
        )
        .reset_index()
    )

    outcome_summary.to_csv(
        OUTPUT_DIR / "outcome_analysis.csv",
        index=False,
    )

    # Representative examples are sampled from the
    # validation partition only, using a fixed seed.
    # Do not export review IDs, reviewer IDs or ASINs.
    sample_frame = results.loc[
        results["is_disagreement"],
        [
            "actual_label",
            "predicted_label",
            "fake_score",
            "word_count",
            "outcome",
        ],
    ].copy()

    original_text = X_val.loc[sample_frame.index]

    sample_frame["original_character_count"] = (
        original_text.str.len().to_numpy()
    )

    sample_frame["review_excerpt"] = (
        original_text.str.slice(0, 240).to_numpy()
    )

    sample_frame["excerpt_was_truncated"] = (
        sample_frame["original_character_count"] > 240
    )

    samples = (
        sample_frame.groupby("outcome", group_keys=False)
        .sample(
            n=min(10, len(sample_frame) // 2),
            random_state=42,
        )
    )

    # Review excerpts may contain user-generated personal
    # information. Keep this file local and out of Git.
    samples.to_csv(
        OUTPUT_DIR / "error_samples_private.csv",
        index=False,
    )

    print("\n=== VALIDATION RESULTS ===")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Macro-F1: {metrics['macro_f1']:.4f}")

    print("\nConfusion matrix:")
    print(matrix)

    print(f"\nFalse positives: {fp:,}")
    print(f"False negatives: {fn:,}")
    print(
        "Total candidate-label disagreements: "
        f"{metrics['total_disagreements']:,}"
    )

    print("\n=== REVIEW LENGTH ANALYSIS ===")
    print(length_summary.to_string(index=False))

    print("\n=== SCORE ANALYSIS ===")
    print(score_summary.to_string(index=False))

    print(f"\nResults saved to: {OUTPUT_DIR}")
    print("Test dataset: NOT ACCESSED")


if __name__ == "__main__":
    main()
