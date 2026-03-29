"""Pydantic schemas — API request/response models."""

from datetime import date, datetime

from pydantic import BaseModel, Field


# --- Auth ---

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    display_name: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=8)
    invite_code: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    username: str
    display_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Items ---

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    category: str = Field(..., pattern=r"^(pokemon|sports|mtg|coins|sealed|apparel|other)$")
    description: str | None = None
    grade: str | None = None
    purchase_price: float | None = None
    purchase_date: date | None = None
    catalog_ref: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    search_override: str | None = None


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    grade: str | None = None
    purchase_price: float | None = None
    purchase_date: date | None = None
    catalog_ref: str | None = None
    tags: list[str] | None = None
    metadata: dict | None = None
    pinned_value: float | None = None
    search_override: str | None = None


class ItemResponse(BaseModel):
    id: str
    name: str
    category: str
    description: str | None
    grade: str | None
    purchase_price: float | None
    purchase_date: date | None
    catalog_ref: str | None
    tags: list[str] | None
    metadata: dict | None
    photos: list[str] | None
    pinned_value: float | None
    search_override: str | None
    created_at: datetime
    current_value: float | None = None
    current_confidence: float | None = None
    value_change_pct: float | None = None

    model_config = {"from_attributes": True}


# --- Appraisals ---

class AppraisalCreate(BaseModel):
    price: float = Field(..., gt=0)
    source: str = "manual"
    source_url: str | None = None
    confidence: float = Field(default=0.5, ge=0, le=1)
    grade_specific: bool = False


class AppraisalResponse(BaseModel):
    id: str
    item_id: str
    price: float
    currency: str
    source: str
    source_url: str | None
    confidence: float
    grade_specific: bool
    composite_price: float | None
    composite_confidence: float | None
    timestamp: datetime

    model_config = {"from_attributes": True}


# --- Troves ---

class TroveCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    item_ids: list[str] = Field(default_factory=list)


class TroveResponse(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime
    item_count: int = 0
    total_value: float | None = None

    model_config = {"from_attributes": True}


# --- Portfolio (aggregate views) ---

class PortfolioSnapshot(BaseModel):
    timestamp: datetime
    total_value: float
    item_count: int
    confidence: float  # average confidence across items


class PortfolioSummary(BaseModel):
    total_value: float | None
    total_cost: float | None
    total_gain: float | None
    gain_pct: float | None
    item_count: int
    high_confidence_count: int  # items with fresh, multi-source valuations
    history: list[PortfolioSnapshot]
