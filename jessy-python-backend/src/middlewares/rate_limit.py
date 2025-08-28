"""
Rate limiting middleware using SlowAPI and Redis for persistence.
Provides different rate limits for different endpoint types.
"""

import redis.asyncio as redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import os
from typing import Callable
import logging

logger = logging.getLogger("rate_limit")

# Redis connection for rate limiting
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

async def test_redis_connection():
    """Test Redis connection during startup"""
    try:
        test_client = redis.from_url(REDIS_URL, decode_responses=True)
        await test_client.ping()
        await test_client.aclose()
        return True
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Rate limiting will use in-memory storage.")
        return False

# Initialize (connection will be tested when actually used)
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    print(f"Redis client initialized (connection will be tested on first use)")
except Exception as e:
    logger.warning(f"Redis client initialization failed: {e}. Rate limiting will use in-memory storage.")
    redis_client = None

#rate limiting is being done per IP address
def get_redis_key_func(request: Request) -> str:
    """
    Generate a unique key for rate limiting based on IP address and endpoint.
    For authenticated users, could be enhanced to use user ID.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = get_remote_address(request)
    
    # Include endpoint path for different rate limits per endpoint
    endpoint = request.url.path
    return f"rate_limit:{ip}:{endpoint}"

def get_redis_storage():
    """Get Redis storage for rate limiting if available, otherwise None for in-memory."""
    if redis_client:
        return redis_client
    return None

# Create limiter instance
limiter = Limiter(
    key_func=get_redis_key_func,
    storage_uri=REDIS_URL if redis_client else None
)

# Custom rate limit exceeded handler
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded errors.
    Returns consistent JSON error response.
    """
    response = JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": f"Rate limit exceeded: {exc.detail}",
        }
    )
    # Optionally set a generic Retry-After header if you want
    response.headers["Retry-After"] = "60"
    return response

# Rate limit decorators for different endpoint types
def auth_rate_limit():
    """Strict rate limiting for authentication endpoints"""
    return limiter.limit("5/minute")

def api_rate_limit():
    """Standard rate limiting for general API endpoints"""
    return limiter.limit("60/minute")

def voice_rate_limit():
    """Rate limiting for voice processing endpoints (more expensive operations)"""
    return limiter.limit("10/minute")

def public_rate_limit():
    """Relaxed rate limiting for public endpoints"""
    return limiter.limit("100/minute")

async def check_redis_health() -> bool:
    """Check if Redis connection is healthy"""
    if not redis_client:
        logger.info("Redis client not initialized")
        return False
    
    try:
        await redis_client.ping()
        logger.info("Redis health check: CONNECTED")
        return True
    except Exception as e:
        logger.warning(f"Redis health check: DISCONNECTED - {e}")
        return False

# Rate limiting middleware class for more complex scenarios
class RateLimitMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Skip rate limiting for health checks and docs
            if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
                await self.app(scope, receive, send)
                return
            
            # Apply stricter limits to auth endpoints
            if request.url.path.startswith("/auth/"):
                # This will be handled by the auth_rate_limit decorator
                pass
                
        await self.app(scope, receive, send)
