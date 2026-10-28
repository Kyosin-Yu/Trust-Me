from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.contracts.review_request import ReviewAnalysisRequest
from app.modules.review_intelligence.evidence_adapter import (
    build_review_evidence,
)
from app.modules.review_intelligence.inference import ReviewPrediction


def make_request():
    return ReviewAnalysisRequest(
        schema_version="1.0",
        analysis_id=uuid4(),
        product_id="TEST-PRODUCT",
        source_type="manual",
        reviews=[
            {"review_id": "R001", "text": "Good product."},
            {"review_id": "R002", "text": "Arrived damaged."},
            {"review_id": "R003", "text": "Works as expected."},
        ],
        requested_at=datetime.now(timezone.utc),
    )


def make_predictions(labels=(1, 0, 1)):
    return [
        ReviewPrediction(
            review_id=f"R{i:03d}",
            candidate_fake_score=0.80 if label else 0.20,
            candidate_label=label,
            classification_threshold=0.65,
            model_version="review_classifier_v1",
        )
        for i, label in enumerate(labels, start=1)
    ]


def test_evidence_aggregation():
    request = make_request()
    evidence = build_review_evidence(
        request,
        make_predictions(),
    )

    assert evidence.analysis_id == request.analysis_id
    assert evidence.product_id == request.product_id
    assert evidence.status.value == "partial"

    assert evidence.total_reviews == 3
    assert evidence.analyzed_reviews == 3
    assert evidence.suspicious_review_count == 2

    assert len(evidence.findings) == 1
    assert evidence.findings[0].review_ids == ["R001", "R003"]

    assert evidence.model_version == "review_classifier_v1"


def test_unperformed_capabilities_remain_unknown():
    evidence = build_review_evidence(
        make_request(),
        make_predictions(),
    )

    assert evidence.capability_status["review_classification"].value == "completed"
    assert evidence.capability_status["sentiment_analysis"].value == "not_performed"
    assert evidence.capability_status["duplicate_detection"].value == "not_performed"

    assert evidence.positive_count is None
    assert evidence.neutral_count is None
    assert evidence.negative_count is None
    assert evidence.duplicate_review_count is None


def test_no_suspicious_predictions():
    evidence = build_review_evidence(
        make_request(),
        make_predictions((0, 0, 0)),
    )

    assert evidence.suspicious_review_count == 0
    assert evidence.findings == []


def test_missing_prediction_rejected():
    with pytest.raises(ValueError, match="must match"):
        build_review_evidence(
            make_request(),
            make_predictions()[:2],
        )


def test_duplicate_prediction_id_rejected():
    predictions = make_predictions()
    predictions[1] = predictions[1].model_copy(
        update={"review_id": "R001"}
    )

    with pytest.raises(ValueError, match="must match"):
        build_review_evidence(
            make_request(),
            predictions,
        )


def test_inconsistent_model_versions_rejected():
    predictions = make_predictions()
    predictions[1] = predictions[1].model_copy(
        update={"model_version": "different_model"}
    )

    with pytest.raises(ValueError, match="same model version"):
        build_review_evidence(
            make_request(),
            predictions,
        )


def test_inconsistent_candidate_label_rejected():
    predictions = make_predictions()

    predictions[0] = predictions[0].model_copy(
        update={"candidate_label": 0}
    )

    with pytest.raises(
        ValueError,
        match="Inconsistent candidate label",
    ):
        build_review_evidence(
            make_request(),
            predictions,
        )


def test_non_frozen_threshold_rejected():
    predictions = make_predictions()

    predictions[0] = predictions[0].model_copy(
        update={"classification_threshold": 0.50}
    )

    with pytest.raises(
        ValueError,
        match="frozen threshold",
    ):
        build_review_evidence(
            make_request(),
            predictions,
        )
