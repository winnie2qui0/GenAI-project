from pydantic import BaseModel, Field
from typing import Optional, Any
import uuid


class ProcurementItemSpec(BaseModel):
    additional_specs: Optional[dict[str, Any]] = None


class ProcurementItem(BaseModel):
    product_name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    quantity: int = 1
    max_price: Optional[float] = None
    currency: str = "USD"
    max_lead_time_days: Optional[int] = None
    moq_acceptable: int = 1
    specs: Optional[ProcurementItemSpec] = None


class ProcurementRequestCreate(BaseModel):
    input_text: Optional[str] = None
    user_id: str = "demo_user"


class ProcurementConfirm(BaseModel):
    items: list[ProcurementItem]


class DecisionRequest(BaseModel):
    action: str = Field(..., pattern="^(accept|override|re_search|reject)$")
    chosen_listing_id: Optional[uuid.UUID] = None
    override_reason: Optional[str] = None
