"""
PACIN Mock Data Provider API
Simulates 5 financial data provider companies for testing the PACIN Key Transformer.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from auth import API_KEYS, require_source, validate_api_key
from data.fixtures import (
    BANK_DATA, DATA_STORES, INSURANCE_DATA, MOMO_DATA,
    MONTHS, SUBJECT_PROFILES, TELECOM_DATA, UTILITY_DATA, VALID_SUBJECTS,
)
from models import (
    DateRange, ErrorResponse, HealthResponse, PACINEnvelope,
    ResponseMetadata, SubjectInfo, WebhookRegisterRequest,
)
from webhooks import fire_webhook, get_events, register_webhook

logger = logging.getLogger("pacin-mock-api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print("  PACIN Mock Data Provider API - Starting Up")
    print("=" * 60)
    for sid in VALID_SUBJECTS:
        p = SUBJECT_PROFILES[sid]
        print(f"    - {sid}: {p['name']} ({p['district']})")
    print(f"  Data range: {MONTHS[0]} to {MONTHS[-1]} ({len(MONTHS)} months)")
    for source, key in API_KEYS.items():
        print(f"    {source:12s} -> {key}")
    print("=" * 60)
    yield

app = FastAPI(
    title="PACIN Mock Data Provider API",
    description="Simulates 5 Rwandan financial data providers for testing the PACIN Key Transformer.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def _now_iso(): return datetime.now(timezone.utc).isoformat()
def _validate_subject(subject_id):
    if subject_id not in VALID_SUBJECTS:
        raise HTTPException(status_code=404, detail=f"Subject '{subject_id}' not found. Valid: {VALID_SUBJECTS}")
def _envelope(source_type, subject_id, data, record_count):
    return PACINEnvelope(source_type=source_type.upper(), subject_id=subject_id, fetched_at=_now_iso(), data=data,
        metadata=ResponseMetadata(record_count=record_count, date_range=DateRange(**{"from": MONTHS[0]+"-01", "to": MONTHS[-1]+"-01"}))).model_dump(by_alias=True)

@app.get("/health", response_model=HealthResponse, tags=["Discovery"])
def health(): return HealthResponse(subjects_loaded=len(VALID_SUBJECTS), sources=list(API_KEYS.keys()))

@app.get("/subjects", tags=["Discovery"])
def list_subjects(nid: str = None):
    """List all test subjects. Pass ?nid= to filter by 16-digit National ID."""
    results = []
    for sid, p in SUBJECT_PROFILES.items():
        subject = SubjectInfo(
            subject_id=sid,
            name=p["name"],
            age=p["age"],
            district=p["district"],
            city=p["city"],
            national_id=p.get("national_id"),
            profile_type="good_credit" if sid == "PACIN_TEST_001" else "risky_thin_file",
        )
        results.append(subject)
    if nid:
        results = [s for s in results if s.national_id == str(nid).strip()]
    return results


@app.get("/subjects/by-nid/{nid}", tags=["Discovery"])
def get_subject_by_nid(nid: str):
    """Lookup a test subject by their 16-digit Rwanda National ID."""
    clean_nid = str(nid).strip()
    for sid, p in SUBJECT_PROFILES.items():
        if p.get("national_id") == clean_nid:
            return SubjectInfo(
                subject_id=sid,
                name=p["name"],
                age=p["age"],
                district=p["district"],
                city=p["city"],
                national_id=p.get("national_id"),
                profile_type="good_credit" if sid == "PACIN_TEST_001" else "risky_thin_file",
            )
    raise HTTPException(
        status_code=404,
        detail=f"No test subject found for NID '{clean_nid}'. "
               f"Valid NIDs: {[p.get('national_id') for p in SUBJECT_PROFILES.values()]}",
    )

@app.get("/momo/{subject_id}", tags=["MoMo"])
def get_momo(subject_id: str, _=Depends(require_source("momo"))):
    _validate_subject(subject_id)
    d = MOMO_DATA[subject_id]
    return _envelope("momo", subject_id, d, sum(m["summary"]["transaction_count"] for m in d))

@app.get("/momo/{subject_id}/summary", tags=["MoMo"])
def get_momo_summary(subject_id: str, _=Depends(require_source("momo"))):
    _validate_subject(subject_id)
    d = MOMO_DATA[subject_id]
    return _envelope("momo", subject_id, {"monthly_summaries": [{"month": m["month"], **m["summary"]} for m in d]}, len(d))

@app.get("/bank/{subject_id}", tags=["Bank"])
def get_bank(subject_id: str, _=Depends(require_source("bank"))):
    _validate_subject(subject_id)
    b = BANK_DATA[subject_id]
    return _envelope("bank", subject_id, b, sum(len(s["transactions"]) for s in b["statements"]))

@app.get("/bank/{subject_id}/loans", tags=["Bank"])
def get_bank_loans(subject_id: str, _=Depends(require_source("bank"))):
    _validate_subject(subject_id)
    return _envelope("bank", subject_id, {"loan_accounts": BANK_DATA[subject_id]["loan_accounts"]}, len(BANK_DATA[subject_id]["loan_accounts"]))

@app.get("/utility/{subject_id}", tags=["Utility"])
def get_utility(subject_id: str, _=Depends(require_source("utility"))):
    _validate_subject(subject_id)
    u = UTILITY_DATA[subject_id]
    return _envelope("utility", subject_id, u, sum(len(a["bills"]) for a in u["accounts"]))

@app.get("/insurance/{subject_id}", tags=["Insurance"])
def get_insurance(subject_id: str, _=Depends(require_source("insurance"))):
    _validate_subject(subject_id)
    i = INSURANCE_DATA[subject_id]
    return _envelope("insurance", subject_id, i, len(i["policies"]))

@app.get("/telecom/{subject_id}", tags=["Telecom"])
def get_telecom(subject_id: str, _=Depends(require_source("telecom"))):
    _validate_subject(subject_id)
    t = TELECOM_DATA[subject_id]
    return _envelope("telecom", subject_id, t, len(t["months"]))

@app.post("/webhook/register", tags=["Webhooks"])
def webhook_register(req: WebhookRegisterRequest, _=Depends(validate_api_key)):
    return {"status": "registered", "registration": register_webhook(req)}

@app.post("/webhook/test/{source_type}", tags=["Webhooks"])
async def webhook_test(source_type: str, _=Depends(validate_api_key)):
    if source_type not in API_KEYS: raise HTTPException(status_code=400, detail=f"Invalid: {source_type}")
    return await fire_webhook(source_type, "PACIN_TEST_001", {"test": True, "triggered_at": _now_iso()})

@app.get("/webhook/events/{source_type}", tags=["Webhooks"])
def webhook_events(source_type: str, _=Depends(validate_api_key)):
    if source_type not in API_KEYS: raise HTTPException(status_code=400, detail=f"Invalid: {source_type}")
    events = get_events(source_type)
    return {"source_type": source_type, "event_count": len(events), "events": events}

if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8000)
