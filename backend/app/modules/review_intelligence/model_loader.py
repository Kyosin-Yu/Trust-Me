import hashlib
import json
from functools import lru_cache
from pathlib import Path

import joblib
from sklearn.calibration import CalibratedClassifierCV


PROJECT_ROOT = Path(__file__).resolve().parents[4]

MODEL_DIR = PROJECT_ROOT / "models" / "review_classifier"

MODEL_PATH = MODEL_DIR / "review_classifier_v1.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

EXPECTED_MODEL_VERSION = "review_classifier_v1"
EXPECTED_THRESHOLD = 0.65
EXPECTED_CLASSES = [0, 1]


def calculate_sha256(path: Path) -> str:
    """Calculate the SHA-256 checksum of the model file."""

    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def verify_model_artifact() -> dict:
    """Verify trusted model metadata before deserialization."""

    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Review classifier artifact not found: {MODEL_PATH}"
        )

    if not METADATA_PATH.is_file():
        raise FileNotFoundError(
            f"Model metadata not found: {METADATA_PATH}"
        )

    with METADATA_PATH.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    if metadata.get("model_version") != EXPECTED_MODEL_VERSION:
        raise ValueError("Unexpected review classifier version.")

    if metadata.get("artifact_filename") != MODEL_PATH.name:
        raise ValueError("Model artifact filename mismatch.")

    if metadata.get("classification_threshold") != EXPECTED_THRESHOLD:
        raise ValueError("Frozen classification threshold mismatch.")

    if metadata.get("classes") != EXPECTED_CLASSES:
        raise ValueError("Model class labels mismatch.")

    if metadata.get("calibration_method") != "sigmoid":
        raise ValueError("Unexpected calibration method.")

    if metadata.get("calibration_seed") != 42:
        raise ValueError("Unexpected calibration seed.")

    if metadata.get("calibration_folds") != 3:
        raise ValueError("Unexpected number of calibration folds.")

    if metadata.get("calibration_ensemble") is not True:
        raise ValueError("Unexpected calibration ensemble setting.")

    actual_checksum = calculate_sha256(MODEL_PATH)

    if actual_checksum != metadata.get("artifact_sha256"):
        raise ValueError("Model artifact SHA-256 mismatch.")

    return metadata


@lru_cache(maxsize=1)
def load_review_classifier():
    """
    Load the trusted calibrated classifier once per process.

    Never load model paths provided by API users.
    """

    metadata = verify_model_artifact()

    # joblib deserialization must only be used with trusted artifacts.
    model = joblib.load(MODEL_PATH)

    if not isinstance(model, CalibratedClassifierCV):
        raise TypeError("Unexpected model artifact type.")

    if list(model.classes_) != EXPECTED_CLASSES:
        raise ValueError("Loaded model has unexpected class labels.")

    return model, metadata
