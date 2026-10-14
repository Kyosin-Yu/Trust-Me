from datetime import date, datetime
from enum import Enum
from uuid import UUID
from pydantic import AwareDatetime, BaseModel, Field, ConfigDict, field_validator, model_validator

class ReviewSourceType(str, Enum):
    MANUAL = "manual"
    UPLOAD = "upload"
    URL = "url"

class ReviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    review_id: str = Field(min_length=1)
    text: str = Field(min_length=1, max_length=10000)
    rating: float | None = Field(default=None, ge=1, le=5)
    review_date: date | None = None
    reviewer_id: str | None = None
    verified_purchase: bool | None = None
    language: str | None = None
    source_review_id: str | None = None
    
    @field_validator("text")
    @classmethod
    def validate_review_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Review text cannot be empty or whitespace only")
        return value

    @field_validator("review_id")
    @classmethod
    def validate_review_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Review ID cannot be empty or whitespace only")
        return value


class SourceMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    platform: str | None = None
    source_url: str | None = None
    collected_at: datetime | None = None


class ReviewAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str = Field(pattern=r"^1\.0$")
    analysis_id: UUID
    product_id: str = Field(min_length=1)
    source_type: ReviewSourceType
    reviews: list[ReviewInput] = Field(
        min_length=1,
        max_length=500
    )

    source_metadata: SourceMetadata | None = None
    requested_at: AwareDatetime

    #Validate product_id
    @field_validator("product_id")
    @classmethod
    def validate_product_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Product ID cannot be empty or whitespace only")
        return value

    #Validate duplicate review_id 
    @model_validator(mode="after")
    def validate_review_ids(self):
        ids = [review.review_id for review in self.reviews]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate review_id values are not allowed")
        return self
