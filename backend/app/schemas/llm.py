from pydantic import BaseModel
from typing import Optional, Any


class ExtractedItem(BaseModel):
    product_name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    quantity: int = 1
    max_price: Optional[float] = None
    currency: str = "USD"
    max_lead_time_days: Optional[int] = None
    moq_acceptable: int = 1
    specs: Optional[dict[str, Any]] = None


class ExtractionResult(BaseModel):
    items: list[ExtractedItem]
    missing_info: list[str] = []
    confidence: str = "medium"


class MatchingJudgment(BaseModel):
    is_same_product: bool
    confidence: float
    reasoning: str


class ExplanationRequest(BaseModel):
    user_requirement: str
    ranked_results: list[dict[str, Any]]
    anomalies: list[dict[str, Any]]
