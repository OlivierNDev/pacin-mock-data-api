import hashlib, hmac, json
from collections import defaultdict
from datetime import datetime, timezone
import httpx
from models import WebhookRegisterRequest, WebhookRegistration

_registrations: dict[str, WebhookRegistration] = {}
_event_log: dict[str, list[dict]] = defaultdict(list)
MAX_EVENTS = 50

def register_webhook(req: WebhookRegisterRequest) -> WebhookRegistration:
    reg = WebhookRegistration(url=req.url, source_type=req.source_type, secret=req.secret,
        registered_at=datetime.now(timezone.utc).isoformat())
    _registrations[req.source_type] = reg
    return reg

def get_registration(source_type): return _registrations.get(source_type)
def get_events(source_type): return _event_log[source_type][-MAX_EVENTS:]

def _sign_payload(payload, secret):
    raw = json.dumps(payload, sort_keys=True, default=str).encode()
    return f"sha256={hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()}"

async def fire_webhook(source_type, subject_id, payload_data):
    reg = _registrations.get(source_type)
    if not reg: return {"fired": False, "reason": f"No webhook for {source_type}"}
    payload = {"summary": payload_data}
    sig = _sign_payload(payload, reg.secret)
    now = datetime.now(timezone.utc).isoformat()
    event = {"event": "data.updated", "source_type": source_type.upper(), "subject_id": subject_id,
        "timestamp": now, "signature": sig, "payload": payload}
    _event_log[source_type].append(event)
    if len(_event_log[source_type]) > MAX_EVENTS: _event_log[source_type] = _event_log[source_type][-MAX_EVENTS:]
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(reg.url, json=event, headers={"Content-Type": "application/json", "X-PACIN-Signature": sig})
        return {"fired": True, "status_code": resp.status_code, "event": event}
    except httpx.HTTPError as e:
        return {"fired": True, "delivery_error": str(e), "event": event}
