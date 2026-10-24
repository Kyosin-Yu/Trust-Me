from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from review_dataset_loader import load_config, load_partition
EXPERIMENT_ID = "review_tfidf_linear_svm_v1"

def build_svm_pipeline(config):
    """Build a text-only TF-IDF + Linear SVM pipeline."""

    tfidf_config = config["tfidf"]

    return Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=tuple(
                    tfidf_config["ngram_range"]
                ),
                max_features=tfidf_config["max_features"],
                min_df=tfidf_config["min_df"],
                lowercase=tfidf_config["lowercase"],
                sublinear_tf=tfidf_config["sublinear_tf"],
                norm=tfidf_config["norm"],
            ),
        ),
        (
            "classifier",
            LinearSVC(
                C=1.0,
                class_weight=None,
                max_iter=5000,
                random_state=config["random_seed"],
            ),
        ),
    ])


def main():
    config = load_config()

    print("=== EXP-04: TF-IDF + LINEAR SVM ===")
    print(f"Experiment: {EXPERIMENT_ID}")
    print("SVM C: 1.0")
    print("Class weighting: None")

    # Only train and validation may be accessed.
    X_train, y_train, _ = load_partition(
        "train", config
    )

    X_val, y_val, _ = load_partition(
        "validation", config
    )

    model = build_svm_pipeline(config)

    print("\nTraining Linear SVM...")
    model.fit(X_train, y_train)
    print("Training: COMPLETED")

    predictions = model.predict(X_val)

    print("\n=== VALIDATION RESULTS ===")

    accuracy = accuracy_score(
        y_val, predictions
    )

    macro_f1 = f1_score(
        y_val,
        predictions,
        average="macro",
        zero_division=0,
    )

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Macro-F1: {macro_f1:.4f}")

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

    print(
        "Confusion Matrix "
        "(rows=actual, columns=predicted):"
    )

    print(
        confusion_matrix(
            y_val,
            predictions,
            labels=[0, 1],
        )
    )

    print("\n=== EXPERIMENT SUMMARY ===")
    print(f"Validation Macro-F1: {macro_f1:.4f}")
    print("EXP-04: COMPLETED")
    print("Test dataset: NOT ACCESSED")


if __name__ == "__main__":
    main()
