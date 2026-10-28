from enum import Enum
from uuid import UUID
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

class AnalysisStatus(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"

class FindingType(str, Enum):
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    DUPLICATE_PATTERN = "duplicate_pattern"
    SENTIMENT_INCONSISTENCY = "sentiment_inconsistency"

class EvidenceMethod(str, Enum):
    RULE_BASED = "rule_based"
    MACHINE_LEARNING = "machine_learning"
    HUMAN_REVIEW = "human_review"


class AnalysisCapability(str, Enum):
    REVIEW_CLASSIFICATION = "review_classification"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    DUPLICATE_DETECTION = "duplicate_detection"


class CapabilityStatus(str, Enum):
    COMPLETED = "completed"
    NOT_PERFORMED = "not_performed"
    FAILED = "failed"


class ReviewFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    finding_type: FindingType
    description: str = Field(min_length=1)
    review_ids: list[str] = Field(min_length=1)
    method: EvidenceMethod | None = None
    method_version: str | None = None

class ReviewEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str = Field(pattern=r"^1\.0$")
    analysis_id: UUID
    product_id: str = Field(min_length=1)
    status: AnalysisStatus
    capability_status: dict[AnalysisCapability, CapabilityStatus] | None = None
    total_reviews: int = Field(ge=0, le=500)
    analyzed_reviews: int = Field(ge=0, le=500)
    positive_count: int | None = Field(ge=0)
    neutral_count: int | None = Field(ge=0)
    negative_count: int | None = Field(ge=0)
    suspicious_review_count: int | None = Field(ge=0)
    duplicate_review_count: int | None = Field(ge=0)
    findings: list[ReviewFinding] = Field(default_factory=list)
    model_version: str | None = None
    analyzed_at: AwareDatetime
    errors: list[str] = Field(default_factory=list)


    @model_validator(mode="after")
    def validate_counts(self):
        if self.analyzed_reviews > self.total_reviews:
            raise ValueError(
                "analyzed_reviews cannot exceed total_reviews"
            )

        sentiment_counts = (
            self.positive_count,
            self.neutral_count,
            self.negative_count,
        )

        available_sentiment_counts = [
            count
            for count in sentiment_counts
            if count is not None
        ]

        if sum(available_sentiment_counts) > self.analyzed_reviews:
            raise ValueError(
                "Sentiment counts cannot exceed analyzed_reviews"
            )

        for field_name in (
            "suspicious_review_count",
            "duplicate_review_count",
        ):
            count = getattr(self, field_name)

            if count is not None and count > self.analyzed_reviews:
                raise ValueError(
                    f"{field_name} cannot exceed analyzed_reviews"
                )

        if self.capability_status is not None:
            capabilities = self.capability_status

            sentiment_status = capabilities.get(
                AnalysisCapability.SENTIMENT_ANALYSIS
            )

            classification_status = capabilities.get(
                AnalysisCapability.REVIEW_CLASSIFICATION
            )

            duplicate_status = capabilities.get(
                AnalysisCapability.DUPLICATE_DETECTION
            )

            if sentiment_status == CapabilityStatus.NOT_PERFORMED:
                if any(count is not None for count in sentiment_counts):
                    raise ValueError(
                        "Unperformed sentiment analysis requires null counts"
                    )

            if classification_status == CapabilityStatus.NOT_PERFORMED:
                if self.suspicious_review_count is not None:
                    raise ValueError(
                        "Unperformed classification requires null count"
                    )

            if duplicate_status == CapabilityStatus.NOT_PERFORMED:
                if self.duplicate_review_count is not None:
                    raise ValueError(
                        "Unperformed duplicate detection requires null count"
                    )
        return self


    @model_validator(mode="after")
    def validate_capability_integrity(self):
        # Legacy evidence may omit capability_status.
        # Newly generated evidence must always populate it.
        if self.capability_status is None:
            return self

        required_capabilities = set(AnalysisCapability)

        if set(self.capability_status) != required_capabilities:
            raise ValueError(
                "Capability status must specify all analysis capabilities"
            )

        capability_fields = {
            AnalysisCapability.REVIEW_CLASSIFICATION: (
                self.suspicious_review_count,
            ),
            AnalysisCapability.SENTIMENT_ANALYSIS: (
                self.positive_count,
                self.neutral_count,
                self.negative_count,
            ),
            AnalysisCapability.DUPLICATE_DETECTION: (
                self.duplicate_review_count,
            ),
        }

        for capability, counts in capability_fields.items():
            status = self.capability_status[capability]

            if status == CapabilityStatus.COMPLETED:
                if any(count is None for count in counts):
                    raise ValueError(
                        f"Completed capability requires numeric counts: "
                        f"{capability.value}"
                    )

            elif status in (
                CapabilityStatus.NOT_PERFORMED,
                CapabilityStatus.FAILED,
            ):
                if any(count is not None for count in counts):
                    raise ValueError(
                        f"Incomplete capability requires null counts: "
                        f"{capability.value}"
                    )

        return self


    @model_validator(mode="after")
    def validate_analysis_status(self):
        if self.status == AnalysisStatus.COMPLETED:
            if (
                self.total_reviews == 0
                or self.analyzed_reviews != self.total_reviews
            ):
                raise ValueError(
                    "Completed analysis must process all submitted reviews"
                )

            if self.capability_status is not None:
                if not self.capability_status or any(
                    status != CapabilityStatus.COMPLETED
                    for status in self.capability_status.values()
                ):
                    raise ValueError(
                        "Completed analysis requires completed capabilities"
                    )

        elif self.status == AnalysisStatus.PARTIAL:
            if not (0 < self.analyzed_reviews <= self.total_reviews):
                raise ValueError(
                    "Partial analysis must process at least one review"
                )

            if self.analyzed_reviews == self.total_reviews:
                if (
                    self.capability_status is None
                    or all(
                        status == CapabilityStatus.COMPLETED
                        for status in self.capability_status.values()
                    )
                ):
                    raise ValueError(
                        "Partial analysis with full review coverage "
                        "requires an incomplete capability"
                    )

        elif self.status == AnalysisStatus.FAILED:
            if self.analyzed_reviews != 0:
                raise ValueError(
                    "Failed analysis cannot contain analyzed reviews"
                )

            if not self.errors or not any(
                error.strip() for error in self.errors
            ):
                raise ValueError(
                    "Failed analysis must include an error message"
                )

        return self
