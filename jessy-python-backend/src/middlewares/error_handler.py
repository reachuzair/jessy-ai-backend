"""
Global error handling middleware for consistent error responses.
Handles different types of exceptions and provides secure error messages.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
import traceback
import os
from typing import Union
from pydantic import ValidationError

logger = logging.getLogger("error_handler")

# Get environment to determine if we should show detailed errors
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
DEBUG_MODE = ENVIRONMENT.lower() in ["development", "dev", "debug"]

class ErrorResponse:
    """Standardized error response structure"""
    
    @staticmethod
    def create_response(
        status_code: int,
        error_type: str,
        message: str,
        details: Union[str, dict] = None,
        request_id: str = None
    ) -> dict:
        """Create a standardized error response"""
        response = {
            "error": error_type,
            "message": message,
            "status_code": status_code,
            "timestamp": None  # Will be added by FastAPI
        }
        
        if request_id:
            response["request_id"] = request_id
            
        if details and DEBUG_MODE:
            response["details"] = details
            
        return response

async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler that catches all unhandled exceptions
    and returns consistent error responses.
    """
    request_id = getattr(request.state, "request_id", None)
    
    # Log the full exception for debugging
    logger.error(
        f"Unhandled exception in {request.method} {request.url.path}: {str(exc)}",
        exc_info=True
    )
    
    # Default error response
    error_response = ErrorResponse.create_response(
        status_code=500,
        error_type="internal_server_error",
        message="An internal server error occurred",
        details=str(exc) if DEBUG_MODE else None,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handler for HTTPException instances.
    Provides consistent formatting for HTTP errors.
    """
    request_id = getattr(request.state, "request_id", None)
    
    # Map status codes to error types
    error_type_map = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        422: "validation_error",
        429: "rate_limit_exceeded",
        500: "internal_server_error"
    }
    
    error_type = error_type_map.get(exc.status_code, "http_error")
    
    error_response = ErrorResponse.create_response(
        status_code=exc.status_code,
        error_type=error_type,
        message=exc.detail,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler for Pydantic validation errors.
    Provides detailed validation error messages.
    """
    request_id = getattr(request.state, "request_id", None)
    
    # Extract validation errors
    validation_errors = []
    for error in exc.errors():
        validation_errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = ErrorResponse.create_response(
        status_code=422,
        error_type="validation_error",
        message="Request validation failed",
        details={"validation_errors": validation_errors} if DEBUG_MODE else None,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handler for SQLAlchemy database errors.
    Provides secure error messages without exposing database details.
    """
    request_id = getattr(request.state, "request_id", None)
    
    # Log the full database error
    logger.error(f"Database error in {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    
    # Handle specific SQLAlchemy errors
    if isinstance(exc, IntegrityError):
        # Handle unique constraint violations, foreign key errors, etc.
        error_message = "A database constraint was violated"
        
        # Try to provide more specific messages for common constraints
        error_str = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        if "unique" in error_str.lower():
            error_message = "A record with this information already exists"
        elif "foreign key" in error_str.lower():
            error_message = "Referenced record does not exist"
            
        error_response = ErrorResponse.create_response(
            status_code=409,
            error_type="database_constraint_error",
            message=error_message,
            details=str(exc) if DEBUG_MODE else None,
            request_id=request_id
        )
        
        return JSONResponse(status_code=409, content=error_response)
    
    # Generic database error
    error_response = ErrorResponse.create_response(
        status_code=500,
        error_type="database_error",
        message="A database error occurred",
        details=str(exc) if DEBUG_MODE else None,
        request_id=request_id
    )
    
    return JSONResponse(status_code=500, content=error_response)

# Middleware to add request IDs for tracking
class RequestIDMiddleware:
    """Middleware to add unique request IDs for error tracking"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            import uuid
            request_id = str(uuid.uuid4())
            scope["state"] = {"request_id": request_id}
        
        await self.app(scope, receive, send)

# Security exception handler for JWT and auth errors
async def security_exception_handler(request: Request, exc: Exception):
    """
    Handler for security-related exceptions.
    Always returns generic messages to avoid information disclosure.
    """
    request_id = getattr(request.state, "request_id", None)
    
    # Log security exceptions for monitoring
    logger.warning(
        f"Security exception in {request.method} {request.url.path}: {str(exc)}",
        extra={"request_id": request_id}
    )
    
    error_response = ErrorResponse.create_response(
        status_code=401,
        error_type="authentication_error",
        message="Authentication failed",
        request_id=request_id
    )
    
    return JSONResponse(status_code=401, content=error_response)
