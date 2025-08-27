from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from slowapi.errors import RateLimitExceeded

# Import routes
from src.routes.auth import router as auth_router
from src.routes.ai_chat import router as ai_chat_router
from src.routes.stt import router as stt_router
from src.routes.voice_chat import router as voice_chat_router

# Import security middleware and handlers
from src.middlewares.rate_limit import limiter, rate_limit_handler
from src.middlewares.error_handler import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    RequestIDMiddleware
)
from src.config.cors import add_cors_middleware #cors is used to allow requests from different origins

# Create FastAPI app
app = FastAPI(
    title="Jessy AI Backend",
    description="AI-powered backend with voice chat, authentication, and AI capabilities",
    version="1.0.0"
)

# Add security middleware
app.add_middleware(RequestIDMiddleware)

# Configure rate limiter
app.state.limiter = limiter

# Add CORS middleware
add_cors_middleware(app)

# Add exception handlers
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include auth routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Include AI chat routes
app.include_router(ai_chat_router, prefix="/ai", tags=["AI Chat"])

# Include STT routes
app.include_router(stt_router, prefix="/stt", tags=["Speech-to-Text"])

# Include Voice Chat routes
app.include_router(voice_chat_router, prefix="/voice", tags=["Voice Chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Jessy AI Backend! Visit /docs for API documentation."}

@app.get("/health")
async def health_check():
    """Health check endpoint to verify all systems are working."""
    from src.middlewares.rate_limit import check_redis_health
    
    health_status = {
        "status": "healthy",
        "security_features": {
            "rate_limiting": "enabled",
            "cors": "enabled",
            "error_handling": "enabled",
            "request_id_middleware": "enabled"
        },
        "redis_connection": "checking..."
    }
    
    # Check Redis connection
    try:
        redis_healthy = await check_redis_health()
        health_status["redis_connection"] = "healthy" if redis_healthy else "disconnected"
    except Exception:
        health_status["redis_connection"] = "error"
    
    return health_status

@app.get("/security-test")
@limiter.limit("2/minute")
async def security_test(request: Request):
    """Test endpoint to verify rate limiting is working."""
    return {
        "message": "This endpoint is rate limited to 2 requests per minute",
        "security": "Rate limiting is working!"
    }
