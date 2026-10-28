
# Review Intelligence — Frozen Model Artifact

## Model Information

- Model version: `review_classifier_v1`
- Dataset version: `strategy_a_v1`
- Model family: TF-IDF + Logistic Regression
- Calibration: Sigmoid, 3-fold product-grouped cross-validation
- Classification threshold: `0.65`
- Positive class: `1` (candidate fake)
- Negative class: `0` (candidate genuine)

The model was trained using research-derived candidate labels.
Its predictions must not be interpreted as confirmed review fraud.

## Required Files

The inference service expects:

models/review_classifier/
- review_classifier_v1.joblib
- model_metadata.json

The `.joblib` artifact is intentionally excluded from Git.

## Setup for Another Developer

1. Clone the Trust Me repository.
2. Obtain the trusted `review_classifier_v1.joblib` artifact from the project team.
3. Copy it into `models/review_classifier/`.
4. Activate the backend Python virtual environment.
5. From `backend/`, run:

   python -c "from app.modules.review_intelligence.model_loader import verify_model_artifact; verify_model_artifact(); print('Model verification: PASSED')"

6. Start the FastAPI backend after verification succeeds.

## Integrity and Compatibility

The loader verifies the artifact SHA-256 checksum against
`model_metadata.json` before deserializing the model.

The model must come from a trusted source because joblib
deserialization can execute Python code.

Use compatible Python, scikit-learn, and dependency versions.
Consult the metadata for the model's recorded environment.

If the binary artifact is regenerated, its checksum may differ.
Do not overwrite the frozen metadata or release artifact without
a deliberate model versioning and verification process.

## Current Scope

Implemented:
- Review-level candidate-suspicious classification
- Calibrated prediction scores
- Structured ReviewEvidence generation
- FastAPI review-analysis endpoint

Not yet implemented:
- Sentiment analysis
- Duplicate-pattern detection
- Automatic product URL review ingestion
- Final Product Trust Score generation
