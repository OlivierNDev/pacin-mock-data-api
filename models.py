from typing import Any, Optional
from pydantic import BaseModel, Field

class DateRange(BaseModel):
    from_date: str = Field(alias="from")
    to_date: str = Field(alias="to")
    model_config = {"populate_by_name": True}

class ResponseMetadata(BaseModel):
    record_count: int
    date_range: DateRange
    currency: str = "RWF"

class PACINEnvelope(BaseModel):
    pacin_partner_version: str = "1.0"
    source_type: str
    subject_id: str
    fetched_at: str
    status: str = "ok"
    data: Any
    metadata: ResponseMetadata

class ErrorResponse(BaseModel):
    pacin_partner_version: str = "1.0"
    status: str = "error"
    error: str
    detail: Optional[str] = None

class WebhookRegisterRequest(BaseModel):
    url: str
    source_type: str
    secret: str

class WebhookRegistration(BaseModel):
    url: str
    source_type: str
    secret: str
    registered_at: str

class WebhookEvent(BaseModel):
    event: str
    source_type: str
    subject_id: str
    timestamp: str
    signature: str
    payload: Any

class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "pacin-mock-data-api"
    version: str = "1.0.0"
    subjects_loaded: int
    sources: list[str]

class SubjectInfo(BaseModel):
    subject_id: str
    name: str
    age: int
    district: str
    city: str
    profile_type: str
    national_id: Optional[str] = None
