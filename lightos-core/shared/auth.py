from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
import os

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# In production, this would be loaded from a database or secure vault.
# For v0.2 readiness, we use a hardcoded demo key and allow overrides via env vars.
VALID_TENANTS = {
    os.getenv("LIGHTOS_API_KEY", "sk-lightos-demo"): "tenant_demo"
}

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        # For local development ease, if no API key is provided and we are in dev mode, allow it?
        # No, strict enforcement for v0.2 readiness.
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Missing X-API-Key header"
        )
    
    tenant_id = VALID_TENANTS.get(api_key)
    if not tenant_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key"
        )
    return tenant_id
