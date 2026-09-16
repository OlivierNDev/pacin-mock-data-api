"""Multi-mode authentication for PACIN Mock API.

Supports three auth styles so any Key Transformer rail can link to this mock:
  1. X-API-Key header          (simple, current default)
  2. Ocp-Apim-Subscription-Key (MTN MoMo / Azure APIM style)
  3. Authorization: Bearer      (OAuth / Mono / Pngme style)

All modes map to the same internal source_type lookup.
"""

from fastapi import HTTPException, Request

# ── Credential registry ─────────────────────────────────────────────────────
# Each mock "company" has three credential identifiers.
# The Key Transformer should store these in its vault.

SOURCE_CREDENTIALS = {
    "momo": {
        "api_key":          "pacin_momo_test_sk_a7f3c9d2e8b14f6a",
        "subscription_key": "momo_subkey_7f3c9d2e8b14f6a93d",
        "client_id":        "a1b2c3d4-momo-4f5e-8a7b-1c2d3e4f5a6b",
        "company":          "MTN MoMo Rwanda (Mock)",
    },
    "bank": {
        "api_key":          "pacin_bank_test_sk_b2e5f8a1d4c7e9f3",
        "subscription_key": "bank_subkey_e5f8a1d4c7e9f3b2d",
        "client_id":        "b2c3d4e5-bank-4a6f-9b8c-2d3e4f5a6b7c",
        "company":          "Bank of Kigali / Equity (Mock)",
    },
    "utility": {
        "api_key":          "pacin_util_test_sk_c4d7e2f9a1b8c3d6",
        "subscription_key": "util_subkey_7e2f9a1b8c3d6c4d",
        "client_id":        "c3d4e5f6-util-4b7a-ac9d-3e4f5a6b7c8d",
        "company":          "RECO / WASAC (Mock)",
    },
    "insurance": {
        "api_key":          "pacin_insur_test_sk_d9e3f6a4b7c2e8f1",
        "subscription_key": "insur_subkey_e3f6a4b7c2e8f1d9",
        "client_id":        "d4e5f6a7-insur-4c8b-bd0e-4f5a6b7c8d9e",
        "company":          "RSSB / Sanlam (Mock)",
    },
    "telecom": {
        "api_key":          "pacin_tel_test_sk_e1f4a8b2c6d9e3f7",
        "subscription_key": "tel_subkey_f4a8b2c6d9e3f7e1",
        "client_id":        "e5f6a7b8-tel-4d9c-ce1f-5a6b7c8d9e0f",
        "company":          "MTN / Airtel Rwanda (Mock)",
    },
}

# Fast reverse-lookup tables
_APIKEY_TO_SOURCE   = {v["api_key"]: k for k, v in SOURCE_CREDENTIALS.items()}
_SUBKEY_TO_SOURCE   = {v["subscription_key"]: k for k, v in SOURCE_CREDENTIALS.items()}
_CLIENTID_TO_SOURCE = {v["client_id"]: k for k, v in SOURCE_CREDENTIALS.items()}

# Keep old API_KEYS dict for backward compat (startup log etc.)
API_KEYS = {k: v["api_key"] for k, v in SOURCE_CREDENTIALS.items()}


def validate_request(request: Request) -> str:
    """Validate incoming request using any supported auth method.
    Returns the source_type string (e.g. 'momo') or raises 401.
    """
    # 1. X-API-Key
    api_key = request.headers.get("X-API-Key") or request.headers.get("x-api-key")
    if api_key and api_key in _APIKEY_TO_SOURCE:
        return _APIKEY_TO_SOURCE[api_key]

    # 2. Ocp-Apim-Subscription-Key (MTN MoMo / Azure APIM style)
    sub_key = (
        request.headers.get("Ocp-Apim-Subscription-Key")
        or request.headers.get("ocp-apim-subscription-key")
    )
    if sub_key and sub_key in _SUBKEY_TO_SOURCE:
        return _SUBKEY_TO_SOURCE[sub_key]

    # 3. Authorization: Bearer {client_id} (OAuth / Mono / Pngme style)
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        bearer = auth_header[7:].strip()
        if bearer in _CLIENTID_TO_SOURCE:
            return _CLIENTID_TO_SOURCE[bearer]

    raise HTTPException(
        status_code=401,
        detail=(
            "Authentication failed. Provide one of:\n"
            "  X-API-Key: <key>\n"
            "  Ocp-Apim-Subscription-Key: <key>\n"
            "  Authorization: Bearer <client_id>"
        ),
    )


def require_source(required: str):
    """FastAPI dependency: validates auth AND checks source type matches endpoint."""
    async def _dep(request: Request) -> str:
        source_type = validate_request(request)
        if source_type != required:
            raise HTTPException(
                status_code=403,
                detail=f"Credentials belong to '{source_type}' but this endpoint requires '{required}'.",
            )
        return source_type
    return _dep


async def validate_api_key(request: Request) -> str:
    """Generic dependency: accepts any valid source credential."""
    return validate_request(request)
