"""
Rate limiting configuration (SlowAPI)
Tiered limits: Development (relaxed), Production (reasonable), with burst support
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings


def get_rate_limit_key(request):
    """
    Use remote address for rate limiting
    Could be enhanced to use user ID for authenticated requests
    """
    return get_remote_address(request)


# Create single limiter instance
limiter = Limiter(key_func=get_rate_limit_key)


# Rate limit configurations by environment
def get_chat_rate_limit() -> str:
    """
    Get appropriate rate limit for chat endpoint based on environment
    
    Returns:
        Rate limit string in SlowAPI format
        Format: "requests/period" or "burst/burst_period;sustained/sustained_period"
    """
    if settings.ENVIRONMENT == "development":
        # Development: Disable rate limiting for testing
        return "1000/minute"
    elif settings.ENVIRONMENT == "production":
        # Production: Burst-aware limits
        # Allow 15 rapid clicks in 10 seconds, but max 60 per minute overall
        return "15/10seconds;60/minute"
    else:
        # Default/staging: Moderate limits
        return "10/10seconds;45/minute"


def get_start_rate_limit() -> str:
    """
    Get appropriate rate limit for session start endpoint
    
    Returns:
        Rate limit string in SlowAPI format
    """
    if settings.ENVIRONMENT == "development":
        # Development: Disable rate limiting for testing
        return "1000/minute"
    else:
        # Production: Allow multiple session starts but prevent abuse
        return "10/minute"


def get_pause_resume_rate_limit() -> str:
    """
    Get appropriate rate limit for pause/resume endpoints
    
    Returns:
        Rate limit string in SlowAPI format
    """
    if settings.ENVIRONMENT == "development":
        # Development: Disable rate limiting for testing
        return "1000/minute"
    else:
        # Production: Reasonable limits for pause/resume actions
        return "20/minute"


