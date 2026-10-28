import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import joblib
import sklearn
from sklearn.calibration import CalibratedClassifierCV

from review_dataset_loader import load_config, load_partition
from train_baseline import build_pipeline
from evaluate_calibration_robustness import create_verified_splits
from evaluate_final_test import verify_frozen_configuration


PROJECT_ROOT = Path(__file__).resolve().parents[1]

FROZEN_CONFIG_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "model_selection"
    / "frozen_model_config.json"
)

MODEL_DIR = PROJECT_ROOT / "models" / "review_classifier"

MODEL_PATH = MODEL_DIR / "review_classifier_v1.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

MODEL_VERSION = "review_classifier_v1"


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def main():
    print("=== DEV-05: FROZEN MODEL EXPORT ===")

    # 1. Validate the frozen model configuration.
    frozen = read_json(FROZEN_CONFIG_PATH)
    baseline = load_config()

    verify_frozen_configuration(frozen, baseline)

    print("Frozen configuration: VERIFIED")
    print("Dataset version:", frozen["dataset_version"])

    # Prevent accidentally replacing an existing release.
    if MODEL_PATH.exists() or METADATA_PATH.exists():
        raise FileExistsError(
            "Model artifact or metadata already exists. "
            "Do not overwrite a released model automatically."
        )

    # 2. Load training data only.
    X_train, y_train, train_df = load_partition(
        "train", baseline
    )

    print(f"Training reviews: {len(X_train):,}")
    print("Validation/test partitions: NOT ACCESSED")

    calibration = frozen["calibration"]

    # 3. Reconstruct the frozen grouped calibration folds.
    splits, fold_records = create_verified_splits(
        X_train,
        y_train,
        train_df[calibration["group_column"]],
        calibration["random_state"],
    )

    if len(splits) != calibration["n_splits"]:
        raise ValueError("Calibration fold count mismatch.")

    if any(
        record["product_overlap"] != 0
        for record in fold_records
    ):
        raise ValueError("Product overlap detected in calibration.")

    print("Calibration folds:", len(splits))
    print("Product overlap: 0")

    # 4. Fit the selected calibrated classifier.
    model = CalibratedClassifierCV(
        estimator=build_pipeline(baseline),
        method=calibration["method"],
        cv=splits,
        ensemble=calibration["ensemble"],
        n_jobs=1,
    )

    print("\nTraining frozen calibrated classifier...")
    model.fit(X_train, y_train)

    if list(model.classes_) != [0, 1]:
        raise ValueError("Unexpected classifier labels.")

    print("Model training: COMPLETED")

    # 5. Serialize the entire fitted pipeline.
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        model,
        MODEL_PATH,
        compress=3,
    )

    checksum = calculate_sha256(MODEL_PATH)

    # 6. Save non-sensitive artifact metadata.
    metadata = {
        "model_version": MODEL_VERSION,
        "selection_id": frozen["selection_id"],
        "dataset_version": frozen["dataset_version"],
        "base_experiment": frozen["base_experiment"],
        "calibration_experiment": frozen["calibration_experiment"],
        "threshold_experiment": frozen["threshold_experiment"],
        "training_reviews": int(len(X_train)),
        "artifact_filename": MODEL_PATH.name,
        "artifact_sha256": checksum,
        "classes": [int(value) for value in model.classes_],
        "positive_class": frozen["classification"]["positive_class"],
        "classification_threshold": frozen["classification"]["threshold"],
        "calibration_method": calibration["method"],
        "calibration_seed": calibration["random_state"],
        "calibration_folds": len(splits),
        "calibration_ensemble": calibration["ensemble"],
        "sklearn_version": sklearn.__version__,
        "python_version": platform.python_version(),
        "exported_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "training_partition": "train",
        "validation_test_accessed": False,
        "label_interpretation": "research_derived_candidate_labels",
    }

    with METADATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    print("\n=== MODEL ARTIFACT ===")
    print("Model:", MODEL_PATH)
    print("Metadata:", METADATA_PATH)
    print("SHA-256:", checksum)
    print("Frozen threshold:", metadata["classification_threshold"])
    print("Export: COMPLETED")
    print("Test dataset: NOT ACCESSED")


if __name__ == "__main__":
    main()
