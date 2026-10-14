
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
    total_reviews: int = Field(ge=0, le=500)
    analyzed_reviews: int = Field(ge=0, le=500)
    positive_count: int = Field(ge=0)
    neutral_count: int = Field(ge=0)
    negative_count: int = Field(ge=0)
    suspicious_review_count: int = Field(ge=0)
    duplicate_review_count: int = Field(ge=0)
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
        sentiment_total = (
            self.positive_count + 
            self.neutral_count + 
            self.negative_count
        )
        if sentiment_total > self.analyzed_reviews:
            raise ValueError(
                "Sentiment counts cannot exceed analyzed_reviews"
            )
        if self.suspicious_review_count > self.analyzed_reviews:
            raise ValueError(
                "suspicious_review_count cannot exceed analyzed_reviews"
            )
        if self.duplicate_review_count > self.analyzed_reviews:
            raise ValueError(
                "duplicate_review_count cannot exceed analyzed_reviews"
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

        elif self.status == AnalysisStatus.PARTIAL:
            if not (0 < self.analyzed_reviews < self.total_reviews):
                raise ValueError(
                    "Partial analysis must process some, but not all reviews"
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