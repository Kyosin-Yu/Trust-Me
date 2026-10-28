from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api import review_routes
from app.contracts.review_evidence import ReviewEvidence
from app.main import app


client = TestClient(app)


def make_payload():
    return {
        "schema_version": "1.0",
        "analysis_id": str(uuid4()),
        "product_id": "TEST-PRODUCT",
        "source_type": "manual",
        "reviews": [
            {
                "review_id": "R001",
                "text": "The product arrived safely.",
            }
        ],
        "requested_at": datetime.now(timezone.utc).isoformat(),
    }


def test_review_analysis_endpoint_success(monkeypatch):
    payload = make_payload()

    def fake_analyze_reviews(request):
        return ReviewEvidence(
            schema_version="1.0",
            analysis_id=request.analysis_id,
            product_id=request.product_id,
            status="partial",
            capability_status={
                "review_classification": "completed",
                "sentiment_analysis": "not_performed",
                "duplicate_detection": "not_performed",
            },
            total_reviews=1,
            analyzed_reviews=1,
            positive_count=None,
            neutral_count=None,
            negative_count=None,
            suspicious_review_count=1,
            duplicate_review_count=None,
            findings=[],
            model_version="review_classifier_v1",
            analyzed_at=datetime.now(timezone.utc),
            errors=[],
        )

    monkeypatch.setattr(
        review_routes,
        "analyze_reviews",
        fake_analyze_reviews,
    )

    response = client.post(
        "/api/v1/reviews/analyze",
        json=payload,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["analysis_id"] == payload["analysis_id"]
    assert result["product_id"] == "TEST-PRODUCT"
    assert result["status"] == "partial"
    assert result["suspicious_review_count"] == 1

    assert result["capability_status"] == {
        "review_classification": "completed",
        "sentiment_analysis": "not_performed",
        "duplicate_detection": "not_performed",
    }

    assert result["positive_count"] is None
    assert result["duplicate_review_count"] is None


def test_review_analysis_invalid_rating():
    payload = make_payload()
    payload["reviews"][0]["rating"] = 9

    response = client.post(
        "/api/v1/reviews/analyze",
        json=payload,
    )

    assert response.status_code == 422


def test_review_analysis_empty_reviews():
    payload = make_payload()
    payload["reviews"] = []

    response = client.post(
        "/api/v1/reviews/analyze",
        json=payload,
    )

    assert response.status_code == 422


def test_review_analysis_duplicate_ids():
    payload = make_payload()
    payload["reviews"].append(
        {
            "review_id": "R001",
            "text": "Another review.",
        }
    )

    response = client.post(
        "/api/v1/reviews/analyze",
        json=payload,
    )

    assert response.status_code == 422


def test_health_endpoint_still_operates():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
