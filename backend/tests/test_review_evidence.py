from datetime import datetime, timezone
from uuid import uuid4
import pytest
from pydantic import ValidationError
from app.contracts.review_evidence import ReviewEvidence

def valid_evidence():
    """Generate valid sample evidence for testing."""
    return {
        "schema_version": "1.0",
        "analysis_id": str(uuid4()),
        "product_id": "product-001",
        "status": "completed",
        "total_reviews": 10,
        "analyzed_reviews": 10,
        "positive_count": 6,
        "neutral_count": 2,
        "negative_count": 2,
        "suspicious_review_count": 3,
        "duplicate_review_count": 1,
        "findings": [],
        "model_version": "baseline-v1",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "errors": []
    }

def test_valid_review_evidence():
    data = valid_evidence()
    evidence = ReviewEvidence.model_validate(data)
    assert evidence.total_reviews == 10
    assert evidence.analyzed_reviews == 10
    assert evidence.status.value == "completed"


def test_analyzed_reviews_exceed_total():
    data = valid_evidence()
    data["analyzed_reviews"] = 11
    with pytest.raises(ValidationError):
        ReviewEvidence.model_validate(data)

def test_sentiment_counts_exceed_analyzed():
    data = valid_evidence()
    data["positive_count"] = 9
    with pytest.raises(ValidationError):
        ReviewEvidence.model_validate(data)

def test_suspicious_count_exceeds_analyzed():
    data = valid_evidence()
    data["suspicious_review_count"] = 11
    with pytest.raises(ValidationError):
        ReviewEvidence.model_validate(data)

def test_duplicate_count_exceeds_analyzed():
    data = valid_evidence()
    data["duplicate_review_count"] = 11
    with pytest.raises(ValidationError):
        ReviewEvidence.model_validate(data)

def test_negative_review_count():
    data = valid_evidence()
    data["negative_count"] = -1
    with pytest.raises(ValidationError):
        ReviewEvidence.model_validate(data)

def test_analyzed_at_requires_timezone():
    data = valid_evidence()
    data["analyzed_at"] = "2026-10-14T15:30:00"
    with pytest.raises(ValidationError):
        ReviewEvidence.model_validate(data)


@pytest.mark.parametrize(
    "status, total_reviews, analyzed_reviews, errors",
    [
        ("completed", 10, 0, []),
        ("completed", 10, 9, []),
        ("partial", 10, 10, []),
        ("partial", 10, 0, []),
        ("failed", 10, 0, []),
        ("failed", 10, 5, ["Analysis failed"]),
    ]
)
def test_invalid_analysis_status_consistency(
    status, total_reviews, analyzed_reviews, errors
):
    data = valid_evidence()
    data["status"] = status
    data["total_reviews"] = total_reviews
    data["analyzed_reviews"] = analyzed_reviews
    data["errors"] = errors
    # Isolate status validation from count validation.
    data["positive_count"] = 0
    data["neutral_count"] = 0
    data["negative_count"] = 0
    data["suspicious_review_count"] = 0
    data["duplicate_review_count"] = 0
    with pytest.raises(ValidationError):
        ReviewEvidence.model_validate(data)

def test_valid_evidence_method():
    data = valid_evidence()
    data["findings"] = [
        {
            "finding_type": "duplicate_pattern",
            "description": "Two reviews contain similar wording.",
            "review_ids": ["r001", "r002"],
            "method": "rule_based",
            "method_version": "duplicate-detector-v1"
        }
    ]

    evidence = ReviewEvidence.model_validate(data)
    assert len(evidence.findings) == 1
    assert evidence.findings[0].method == "rule_based"
    assert evidence.findings[0].method_version == "duplicate-detector-v1"

def test_invalid_evidence_method():
    data = valid_evidence()
    data["findings"] = [
        {
            "finding_type": "suspicious_pattern",
            "description": "Unusual review wording detected.",
            "review_ids": ["r001"],
            "method": "unkown_method",
            "method_version": "test-v1"
        }
    ]

    with pytest.raises(ValidationError):
        ReviewEvidence.model_validate(data)