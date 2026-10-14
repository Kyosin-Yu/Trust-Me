from datetime import datetime, timezone
from uuid import uuid4
import pytest
from pydantic import ValidationError
from app.contracts.review_request import ReviewAnalysisRequest


def valid_request():
    """Create a valid review analysis request for testing."""
    return {
        "schema_version": "1.0",
        "analysis_id": str(uuid4()),
        "product_id": "product-001",
        "source_type": "manual",
        "reviews": [
            {
                "review_id": "r001",
                "text": "Good quality and fast delivery.",
                "rating": 5
            }
        ],
        "requested_at": datetime.now(timezone.utc).isoformat()
    }


def test_valid_review_request():
    data = valid_request()
    request = ReviewAnalysisRequest.model_validate(data)
    assert request.product_id == "product-001"
    assert len(request.reviews) == 1


def test_invalid_rating():
    data = valid_request()
    data["reviews"][0]["rating"] = 8
    with pytest.raises(ValidationError):
        ReviewAnalysisRequest.model_validate(data)


def test_duplicate_review_ids():
    data = valid_request()

    data["reviews"].append({
        "review_id": "r001",
        "text": "Another review with the same ID.",
        "rating": 4
    })
    with pytest.raises(ValidationError):
        ReviewAnalysisRequest.model_validate(data)


def test_empty_reviews():
    data = valid_request()
    data["reviews"] = []
    with pytest.raises(ValidationError):
        ReviewAnalysisRequest.model_validate(data)


def test_invalid_source_type():
    data = valid_request()
    data["source_type"] = "social_media"
    with pytest.raises(ValidationError):
        ReviewAnalysisRequest.model_validate(data)


def test_whitespace_only_review_text():
    data = valid_request()
    data["reviews"][0]["text"] = "   "
    with pytest.raises(ValidationError):
        ReviewAnalysisRequest.model_validate(data)

@pytest.mark.parametrize("field_name", ["review_id", "product_id"])
def test_whitespace_only_identifiers(field_name):
    data = valid_request()
    if field_name == "review_id":
        data["reviews"][0]["review_id"] = "   "
    else:
        data[field_name] = "   "
    with pytest.raises(ValidationError):
        ReviewAnalysisRequest.model_validate(data)

def test_requested_at_requires_timezone():
    data = valid_request()
    data["requested_at"] = "2026-10-14T14:30:00"

    with pytest.raises(ValidationError):
        ReviewAnalysisRequest.model_validate(data)

@pytest.mark.parametrize("review_count, should_pass", [(1,True), (500, True), (501, False)])
def test_review_batch_size_boundaries(review_count, should_pass):
    data = valid_request()
    data["reviews"] = [
        {
            "review_id": f"r{i:03d}",
            "text": f"Sample review number {i}",
            "rating": 4
        } for i in range(review_count)
    ]
    if should_pass:
        request = ReviewAnalysisRequest.model_validate(data)
        assert len(request.reviews) == review_count
    else:
        with pytest.raises(ValidationError):
            ReviewAnalysisRequest.model_validate(data)