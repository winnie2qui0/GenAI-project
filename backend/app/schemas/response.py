from pydantic import BaseModel
from typing import Optional, Any
import uuid
from datetime import datetime


class ScoreBreakdown(BaseModel):
    price_score: float
    delivery_score: float
    rating_score: float
    trust_score: float


class AnomalyFlag(BaseModel):
    type: str
    severity: str
    message: str


class RankedListing(BaseModel):
    rank: int
    listing_id: uuid.UUID
    source: str
    title: str
    price: float
    currency: str
    price_usd: Optional[float]
    delivery_days: Optional[int]
    rating: Optional[float]
    review_count: Optional[int]
    moq: int
    seller_name: Optional[str]
    final_score: float
    score_breakdown: ScoreBreakdown
    anomalies: list[AnomalyFlag]
    llm_explanation: Optional[str]
    url: str


class ClusterResult(BaseModel):
    cluster_id: uuid.UUID
    canonical_name: str
    confidence: str
    matching_method: Optional[str]
    ranked_listings: list[RankedListing]


class ProcurementRequestResponse(BaseModel):
    request_id: uuid.UUID
    parsed_items: list[dict[str, Any]]
    status: str
    created_at: datetime


class StatusResponse(BaseModel):
    status: str
    progress: dict[str, Any]


class ResultsResponse(BaseModel):
    request_id: uuid.UUID
    clusters: list[ClusterResult]


class DecisionResponse(BaseModel):
    audit_id: uuid.UUID
    message: str
