import numpy as np
import pytest

from app.contracts.review_request import ReviewInput
from app.modules.review_intelligence import inference


class FakeClassifier:
    """Deterministic classifier for testing inference logic."""

    classes_ = np.array([0, 1])

    def __init__(self, scores):
        self.scores = scores

    def predict_proba(self, texts):
        if len(texts) != len(self.scores):
            raise ValueError("Unexpected number of review texts.")

        return np.array(
            [[1.0 - score, score] for score in self.scores],
            dtype=float,
        )


@pytest.fixture
def mock_classifier(monkeypatch):
    def configure(scores):
        classifier = FakeClassifier(scores)

        metadata = {
            "model_version": "review_classifier_v1",
            "positive_class": 1,
            "classification_threshold": 0.65,
        }

        monkeypatch.setattr(
            inference,
            "load_review_classifier",
            lambda: (classifier, metadata),
        )

        return classifier

    return configure


def make_reviews(count):
    return [
        ReviewInput(
            review_id=f"R{i:03d}",
            text=f"Example review number {i}.",
        )
        for i in range(count)
    ]


def test_batch_prediction_and_review_order(mock_classifier):
    mock_classifier([0.20, 0.75, 0.55])

    predictions = inference.predict_reviews(make_reviews(3))

    assert len(predictions) == 3
    assert [p.review_id for p in predictions] == [
        "R000", "R001", "R002"
    ]

    assert [p.candidate_label for p in predictions] == [0, 1, 0]

    assert [
        p.candidate_fake_score for p in predictions
    ] == pytest.approx([0.20, 0.75, 0.55])

    assert all(
        p.model_version == "review_classifier_v1"
        for p in predictions
    )


def test_threshold_boundary(mock_classifier):
    mock_classifier([0.6499, 0.65, 0.6501])

    predictions = inference.predict_reviews(make_reviews(3))

    assert [p.candidate_label for p in predictions] == [0, 1, 1]
    assert all(
        p.classification_threshold == 0.65
        for p in predictions
    )


@pytest.mark.parametrize(
    "invalid_score",
    [float("nan"), float("inf"), -0.1, 1.1],
)
def test_invalid_probabilities_are_rejected(
    mock_classifier,
    invalid_score,
):
    mock_classifier([invalid_score])

    with pytest.raises(ValueError, match="invalid probability"):
        inference.predict_reviews(make_reviews(1))


def test_empty_review_batch_is_rejected():
    with pytest.raises(
        ValueError,
        match="between 1 and 500",
    ):
        inference.predict_reviews([])


def test_duplicate_review_ids_are_rejected():
    reviews = [
        ReviewInput(review_id="R001", text="First review."),
        ReviewInput(review_id="R001", text="Second review."),
    ]

    with pytest.raises(
        ValueError,
        match="Duplicate review IDs",
    ):
        inference.predict_reviews(reviews)


def test_more_than_500_reviews_is_rejected():
    with pytest.raises(
        ValueError,
        match="between 1 and 500",
    ):
        inference.predict_reviews(make_reviews(501))
