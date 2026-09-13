from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEYS = {
    "momo": "pacin_momo_test_sk_a7f3c9d2e8b14f6a",
    "bank": "pacin_bank_test_sk_b2e5f8a1d4c7e9f3",
    "utility": "pacin_util_test_sk_c4d7e2f9a1b8c3d6",
    "insurance": "pacin_insur_test_sk_d9e3f6a4b7c2e8f1",
    "telecom": "pacin_tel_test_sk_e1f4a8b2c6d9e3f7",
}
_KEY_TO_SOURCE = {v: k for k, v in API_KEYS.items()}
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def validate_api_key(api_key: str = Security(api_key_header)) -> str:
    if not api_key or api_key not in _KEY_TO_SOURCE:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    return _KEY_TO_SOURCE[api_key]

def require_source(required: str):
    def _check(source_type: str = Security(validate_api_key)):
        if source_type != required:
            raise HTTPException(status_code=403, detail=f"Key valid for '{source_type}' not '{required}'.")
        return source_type
    return _check
