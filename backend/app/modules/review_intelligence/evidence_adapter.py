from collections import Counter
from datetime import datetime, timezone
from typing import Sequence

from app.contracts.review_request import ReviewAnalysisRequest
from app.contracts.review_evidence import (
    AnalysisCapability,
    AnalysisStatus,
    CapabilityStatus,
    EvidenceMethod,
    FindingType,
    ReviewEvidence,
    ReviewFinding,
)
from app.modules.review_intelligence.inference import ReviewPrediction


def build_review_evidence(
    request: ReviewAnalysisRequest,
    predictions: Sequence[ReviewPrediction],
) -> ReviewEvidence:
    """
    Convert review-level ML predictions into structured evidence.

    Only review classification has been implemented.
    Sentiment and duplicate detection remain unavailable.
    """

    expected_ids = {review.review_id for review in request.reviews}
    actual_ids = [prediction.review_id for prediction in predictions]

    if (
        len(predictions) != len(request.reviews)
        or len(set(actual_ids)) != len(actual_ids)
        or set(actual_ids) != expected_ids
    ):
        raise ValueError(
            "Predictions must match submitted review IDs exactly."
        )


    thresholds = {
        prediction.classification_threshold
        for prediction in predictions
    }

    if thresholds != {0.65}:
        raise ValueError(
            "Predictions must use the frozen threshold of 0.65."
        )

    for prediction in predictions:
        expected_label = int(
            prediction.candidate_fake_score
            >= prediction.classification_threshold
        )

        if prediction.candidate_label != expected_label:
            raise ValueError(
                f"Inconsistent candidate label for "
                f"review {prediction.review_id}."
            )

    model_versions = {
        prediction.model_version
        for prediction in predictions
    }

    if len(model_versions) != 1:
        raise ValueError(
            "All predictions must use the same model version."
        )

    suspicious_ids = [
        prediction.review_id
        for prediction in predictions
        if prediction.candidate_label == 1
    ]

    suspicious_count = len(suspicious_ids)

    findings = []

    if suspicious_ids:
        findings.append(
            ReviewFinding(
                finding_type=FindingType.SUSPICIOUS_PATTERN,
                description=(
                    f"{suspicious_count} of {len(predictions)} reviews "
                    "were classified as candidate suspicious by the "
                    "research-derived review classifier. These "
                    "predictions do not establish confirmed fraud."
                ),
                review_ids=suspicious_ids,
                method=EvidenceMethod.MACHINE_LEARNING,
                method_version=next(iter(model_versions)),
            )
        )

    return ReviewEvidence(
        schema_version="1.0",
        analysis_id=request.analysis_id,
        product_id=request.product_id,
        status=AnalysisStatus.PARTIAL,
        capability_status={
            AnalysisCapability.REVIEW_CLASSIFICATION:
                CapabilityStatus.COMPLETED,
            AnalysisCapability.SENTIMENT_ANALYSIS:
                CapabilityStatus.NOT_PERFORMED,
            AnalysisCapability.DUPLICATE_DETECTION:
                CapabilityStatus.NOT_PERFORMED,
        },
        total_reviews=len(request.reviews),
        analyzed_reviews=len(predictions),
        positive_count=None,
        neutral_count=None,
        negative_count=None,
        suspicious_review_count=suspicious_count,
        duplicate_review_count=None,
        findings=findings,
        model_version=next(iter(model_versions)),
        analyzed_at=datetime.now(timezone.utc),
        errors=[],
    )
