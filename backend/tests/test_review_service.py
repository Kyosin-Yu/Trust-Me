from datetime import datetime, timezone
from uuid import uuid4

from app.contracts.review_request import ReviewAnalysisRequest
from app.contracts.review_evidence import (
    AnalysisCapability,
    AnalysisStatus,
    CapabilityStatus,
)
from app.modules.review_intelligence import service
from app.modules.review_intelligence.inference import ReviewPrediction


def test_review_service_orchestration(monkeypatch):
    request = ReviewAnalysisRequest(
        schema_version="1.0",
        analysis_id=uuid4(),
        product_id="TEST-PRODUCT",
        source_type="manual",
        reviews=[
            {
                "review_id": "R001",
                "text": "The product arrived in good condition.",
            },
            {
                "review_id": "R002",
                "text": "The item stopped working.",
            },
        ],
        requested_at=datetime.now(timezone.utc),
    )

    predictions = [
        ReviewPrediction(
            review_id="R001",
            candidate_fake_score=0.80,
            candidate_label=1,
            classification_threshold=0.65,
            model_version="review_classifier_v1",
        ),
        ReviewPrediction(
            review_id="R002",
            candidate_fake_score=0.20,
            candidate_label=0,
            classification_threshold=0.65,
            model_version="review_classifier_v1",
        ),
    ]

    calls = []

    def fake_predict_reviews(reviews):
        calls.append("inference")
        assert reviews == request.reviews
        return predictions

    original_build_evidence = service.build_review_evidence

    def tracked_build_evidence(request, predictions):
        calls.append("evidence_adapter")
        return original_build_evidence(
            request=request,
            predictions=predictions,
        )

    monkeypatch.setattr(
        service,
        "predict_reviews",
        fake_predict_reviews,
    )

    monkeypatch.setattr(
        service,
        "build_review_evidence",
        tracked_build_evidence,
    )

    evidence = service.analyze_reviews(request)

    assert calls == ["inference", "evidence_adapter"]

    assert evidence.analysis_id == request.analysis_id
    assert evidence.product_id == request.product_id
    assert evidence.status == AnalysisStatus.PARTIAL

    assert evidence.total_reviews == 2
    assert evidence.analyzed_reviews == 2
    assert evidence.suspicious_review_count == 1

    assert evidence.capability_status[
        AnalysisCapability.REVIEW_CLASSIFICATION
    ] == CapabilityStatus.COMPLETED

    assert evidence.capability_status[
        AnalysisCapability.SENTIMENT_ANALYSIS
    ] == CapabilityStatus.NOT_PERFORMED

    assert evidence.capability_status[
        AnalysisCapability.DUPLICATE_DETECTION
    ] == CapabilityStatus.NOT_PERFORMED

    assert evidence.positive_count is None
    assert evidence.duplicate_review_count is None

    assert len(evidence.findings) == 1
    assert evidence.findings[0].review_ids == ["R001"]
