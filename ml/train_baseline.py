import json
import argparse
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.pipeline import Pipeline

from review_dataset_loader import load_config, load_partition


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_pipeline(config):
    tfidf = config["tfidf"]
    lr = config["logistic_regression"]

    return Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=tuple(tfidf["ngram_range"]),
                max_features=tfidf["max_features"],
                min_df=tfidf["min_df"],
                lowercase=tfidf["lowercase"],
                sublinear_tf=tfidf["sublinear_tf"],
                norm=tfidf["norm"],
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                C=lr["C"],
                class_weight=lr["class_weight"],
                max_iter=lr["max_iter"],
                random_state=lr["random_state"],
            ),
        ),
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default=None,
        help="Path to experiment JSON configuration"
        )
    args = parser.parse_args()
    config = load_config(args.config)

    print("=== TF-IDF + LOGISTIC REGRESSION ===")
    print(f"Experiment: {config['experiment_id']}")

    X_train, y_train, _ = load_partition("train", config)
    X_val, y_val, _ = load_partition("validation", config)

    model = build_pipeline(config)

    print("\nTraining model...")
    model.fit(X_train, y_train)

    print("Training: COMPLETED")

    predictions = model.predict(X_val)

    print("\n=== VALIDATION RESULTS ===")
    print(f"Accuracy: {accuracy_score(y_val, predictions):.4f}")
    print(f"Macro-F1: {f1_score(y_val, predictions, average='macro'):.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_val,
            predictions,
            labels=[0, 1],
            target_names=[
                "candidate_genuine",
                "candidate_fake",
            ],
            digits=4,
            zero_division=0,
        )
    )

    print("Confusion Matrix (rows=actual, columns=predicted):")
    print(confusion_matrix(y_val, predictions, labels=[0, 1]))

    print("\nTest dataset: NOT ACCESSED")


if __name__ == "__main__":
    main()
