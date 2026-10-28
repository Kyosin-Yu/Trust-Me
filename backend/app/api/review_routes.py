from fastapi import APIRouter

from app.contracts.review_request import ReviewAnalysisRequest
from app.contracts.review_evidence import ReviewEvidence
from app.modules.review_intelligence.service import analyze_reviews


router = APIRouter(
    prefix="/api/v1/reviews",
    tags=["Review Intelligence"],
)


@router.post(
    "/analyze",
    response_model=ReviewEvidence,
)
def analyze_product_reviews(
    request: ReviewAnalysisRequest,
) -> ReviewEvidence:
    """
    Run Review Intelligence analysis.

    Currently supports candidate-suspicious review classification.
    Sentiment and duplicate detection are not yet implemented.
    """
    return analyze_reviews(request)
