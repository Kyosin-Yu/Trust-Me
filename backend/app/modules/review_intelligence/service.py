from app.contracts.review_request import ReviewAnalysisRequest
from app.contracts.review_evidence import ReviewEvidence

from app.modules.review_intelligence.inference import predict_reviews
from app.modules.review_intelligence.evidence_adapter import (
    build_review_evidence,
)


def analyze_reviews(
    request: ReviewAnalysisRequest,
) -> ReviewEvidence:
    """
    Execute the currently implemented Review Intelligence workflow.

    Current capability:
        - Candidate suspicious review classification

    Not yet implemented:
        - Sentiment analysis
        - Duplicate-pattern detection
    """

    predictions = predict_reviews(request.reviews)

    evidence = build_review_evidence(
        request=request,
        predictions=predictions,
    )

    return evidence
