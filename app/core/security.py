from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    """Validate API key from header."""
    if api_key_header != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )
    return api_key_header 