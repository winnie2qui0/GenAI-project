from typing import Any, Literal

from pydantic import BaseModel, Field


class ParsedItem(BaseModel):
    product_name: str
    brand: str | None = None
    model: str | None = None
    quantity: int = 1
    max_price: float | None = None
    currency: str = "USD"
    max_lead_time_days: int | None = None
    moq_acceptable: int = 1
    specs: dict[str, Any] | None = None


class CreateProcurementBody(BaseModel):
    input_text: str | None = Field(default=None, description="Natural language procurement need")


class ConfirmProcurementBody(BaseModel):
    items: list[ParsedItem]


class DecisionBody(BaseModel):
    action: Literal["accept", "override", "re_search", "reject"]
    chosen_listing_id: str | None = None
    override_reason: str | None = None
