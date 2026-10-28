import math
from typing import Literal, Sequence

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.review_request import ReviewInput
from app.modules.review_intelligence.model_loader import (
    load_review_classifier,
)


class ReviewPrediction(BaseModel):
    """Internal, review-level candidate classification."""

    model_config = ConfigDict(extra="forbid")

    review_id: str = Field(min_length=1)
    candidate_fake_score: float = Field(ge=0.0, le=1.0)
    candidate_label: Literal[0, 1]
    classification_threshold: float = Field(ge=0.0, le=1.0)
    model_version: str = Field(min_length=1)


def predict_reviews(
    reviews: Sequence[ReviewInput],
) -> list[ReviewPrediction]:
    """
    Classify reviews using the frozen calibrated model.

    Label 0 = candidate_genuine
    Label 1 = candidate_fake

    Scores relate to research-derived proxy labels,
    not verified probabilities of review fraud.
    """

    if not 1 <= len(reviews) <= 500:
        raise ValueError(
            "Inference requires between 1 and 500 reviews."
        )

    review_ids = [review.review_id for review in reviews]

    if len(set(review_ids)) != len(review_ids):
        raise ValueError("Duplicate review IDs are not allowed.")

    texts = [review.text for review in reviews]

    model, metadata = load_review_classifier()

    threshold = float(metadata["classification_threshold"])
    model_version = metadata["model_version"]

    positive_class = metadata["positive_class"]

    if positive_class not in model.classes_:
        raise ValueError(
            "Candidate-fake class not found in model."
        )

    positive_index = list(model.classes_).index(positive_class)

    # Batch inference preserves the input review order.
    probabilities = model.predict_proba(texts)

    if probabilities.shape != (len(reviews), len(model.classes_)):
        raise ValueError("Unexpected model probability shape.")

    predictions = []

    for review_id, probability_row in zip(
        review_ids,
        probabilities,
        strict=True,
    ):
        score = float(probability_row[positive_index])

        if not math.isfinite(score) or not 0.0 <= score <= 1.0:
            raise ValueError(
                "Model produced an invalid probability."
            )

        predicted_label = 1 if score >= threshold else 0

        predictions.append(
            ReviewPrediction(
                review_id=review_id,
                candidate_fake_score=score,
                candidate_label=predicted_label,
                classification_threshold=threshold,
                model_version=model_version,
            )
        )

    return predictions
