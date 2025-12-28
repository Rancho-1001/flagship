"""
Authentication module for FlagShip API.
Implements API key-based authentication.
"""
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings
from app.logger import logger

# API Key header name
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# In production, store API keys in database
# For now, using environment variable for simplicity
# Format: API_KEYS=key1,key2,key3
def get_api_keys() -> list[str]:
    """Get valid API keys from environment or config."""
    api_keys_str = getattr(settings, "API_KEYS", "")
    if api_keys_str:
        return [key.strip() for key in api_keys_str.split(",") if key.strip()]
    # Default key for development (should be changed in production)
    return ["dev-api-key-12345"]


def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    Verify API key from request header.
    
    Args:
        api_key: API key from X-API-Key header
    
    Returns:
        The API key if valid
    
    Raises:
        HTTPException: If API key is missing or invalid
    """
    valid_keys = get_api_keys()
    
    if not api_key:
        logger.warning("API request without API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Please provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key not in valid_keys:
        logger.warning(f"Invalid API key attempted: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    logger.debug(f"API key verified successfully")
    return api_key

