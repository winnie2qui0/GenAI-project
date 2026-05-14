from typing import Any

from pydantic import BaseModel, Field


class ExtractedRequirements(BaseModel):
    items: list[dict[str, Any]]
    missing_info: list[str] = Field(default_factory=list)
    confidence: str = "medium"


class MatchingJudgment(BaseModel):
    is_same_product: bool
    confidence: float
    reasoning: str
