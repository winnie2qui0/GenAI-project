from typing import Any

from pydantic import BaseModel, Field


class RequestCreatedResponse(BaseModel):
    request_id: str
    parsed_items: list[dict[str, Any]]
    status: str


class CrawlProgress(BaseModel):
    platforms_crawled: int = 0
    total_platforms: int = 4
    listings_found: int = 0
    clusters_created: int = 0


class ProcurementStatusResponse(BaseModel):
    status: str
    progress: CrawlProgress


class ScoreBreakdown(BaseModel):
    price_score: float
    delivery_score: float
    rating_score: float
    trust_score: float


class ListingRanked(BaseModel):
    rank: int
    listing_id: str
    source: str
    price: float
    currency: str
    price_usd: float | None
    delivery_days: int | None
    rating: float | None
    final_score: float
    score_breakdown: ScoreBreakdown
    anomalies: list[dict[str, Any]]
    llm_explanation: str | None
    url: str


class ClusterResult(BaseModel):
    cluster_id: str
    canonical_name: str
    confidence: str
    ranked_listings: list[ListingRanked]


class ProcurementResultsResponse(BaseModel):
    request_id: str
    clusters: list[ClusterResult]


class DecisionResponse(BaseModel):
    ok: bool = True
    audit_id: str
