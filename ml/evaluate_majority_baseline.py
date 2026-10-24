from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)

from review_dataset_loader import load_config, load_partition


def main():
    config = load_config()

    X_train, y_train, _ = load_partition("train", config)
    X_val, y_val, _ = load_partition("validation", config)

    model = DummyClassifier(strategy="most_frequent")
    model.fit(X_train, y_train)

    predictions = model.predict(X_val)

    print("=== EXP-00: MAJORITY-CLASS BASELINE ===")
    print(f"Training majority class: {model.classes_[model.class_prior_.argmax()]}")

    print(
        f"Accuracy: "
        f"{accuracy_score(y_val, predictions):.4f}"
    )

    print(
        f"Macro-F1: "
        f"{f1_score(y_val, predictions, average='macro'):.4f}"
    )

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

    print("\nMajority-class evaluation: COMPLETED")
    print("Test dataset: NOT ACCESSED")


if __name__ == "__main__":
    main()
