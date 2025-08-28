"""
CORS configuration that reads allowed origins from environment variables.
Provides secure defaults and flexible configuration for different environments.
"""

import os
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Union

class CORSConfig:
    """
    CORS configuration class that handles environment-based settings.
    """
    
    def __init__(self):
        # Get environment
        self.environment = os.getenv("ENVIRONMENT", "production").lower()
        
        # Parse allowed origins from environment
        self.allowed_origins = self._parse_allowed_origins()
        
        # Configure other CORS settings
        self.allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
        self.allowed_methods = self._parse_list("CORS_ALLOWED_METHODS", ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
        self.allowed_headers = self._parse_list("CORS_ALLOWED_HEADERS", [
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "Accept",
            "Origin",
            "X-CSRF-Token"
        ])
        self.exposed_headers = self._parse_list("CORS_EXPOSED_HEADERS", [])
        self.max_age = int(os.getenv("CORS_MAX_AGE", "86400"))  # 24 hours
    
    def _parse_allowed_origins(self) -> List[str]:
        """
        Parse allowed origins from environment variables.
        Supports multiple formats and provides secure defaults.
        """
        origins_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
        
        if not origins_env:
            # Default origins based on environment
            if self.environment in ["development", "dev", "debug"]:
                return [
                    "http://localhost:3000",  # React dev server
                    "http://localhost:3001",  # Alternative React port
                    "http://127.0.0.1:3000",
                    "http://127.0.0.1:3001",
                    "http://localhost:8000",  # FastAPI dev server
                    "http://127.0.0.1:8000"
                ]
            elif self.environment == "staging":
                return [
                    "https://staging.yourdomain.com",
                    "https://staging-api.yourdomain.com"
                ]
            else:  # production
                return [
                    "https://yourdomain.com",
                    "https://www.yourdomain.com",
                    "https://api.yourdomain.com"
                ]
        
        # Parse comma-separated origins from environment
        origins = [origin.strip() for origin in origins_env.split(",")]
        
        # Validate origins (basic validation)
        validated_origins = []
        for origin in origins:
            if origin == "*":
                if self.environment != "development":
                    # Don't allow wildcard in production
                    continue
                validated_origins.append(origin)
            elif origin.startswith(("http://", "https://")):
                validated_origins.append(origin)
            elif origin.startswith("localhost:") or origin.startswith("127.0.0.1:"):
                # Add protocol for localhost
                if self.environment == "development":
                    validated_origins.append(f"http://{origin}")
            else:
                # Assume HTTPS for domain names in production
                if self.environment == "production":
                    validated_origins.append(f"https://{origin}")
                else:
                    # Allow both HTTP and HTTPS in development
                    validated_origins.extend([f"http://{origin}", f"https://{origin}"])
        
        return validated_origins
    
    def _parse_list(self, env_var: str, default: List[str]) -> List[str]:
        """Parse a comma-separated list from environment variable."""
        env_value = os.getenv(env_var, "")
        if not env_value:
            return default
        return [item.strip() for item in env_value.split(",")]
    
    def get_middleware_kwargs(self) -> dict:
        """
        Get the kwargs for CORSMiddleware.
        """
        return {
            "allow_origins": self.allowed_origins,
            "allow_credentials": self.allow_credentials,
            "allow_methods": self.allowed_methods,
            "allow_headers": self.allowed_headers,
            "expose_headers": self.exposed_headers,
            "max_age": self.max_age
        }
    
    def log_configuration(self, logger):
        """Log the CORS configuration for debugging."""
        logger.info(f"CORS Configuration:")
        logger.info(f"  Environment: {self.environment}")
        logger.info(f"  Allowed Origins: {self.allowed_origins}")
        logger.info(f"  Allow Credentials: {self.allow_credentials}")
        logger.info(f"  Allowed Methods: {self.allowed_methods}")
        logger.info(f"  Allowed Headers: {self.allowed_headers}")
        logger.info(f"  Max Age: {self.max_age}")

# Create global CORS configuration instance
cors_config = CORSConfig()

def add_cors_middleware(app):
    """
    Add CORS middleware to FastAPI application with environment-based configuration.
    """
    import logging
    logger = logging.getLogger("cors")
    
    # Log configuration in development
    if cors_config.environment == "development":
        cors_config.log_configuration(logger)
    
    app.add_middleware(
        CORSMiddleware,
        **cors_config.get_middleware_kwargs()
    )
    
    logger.info("CORS middleware added to application")
    
    return app

# Environment-specific CORS configurations
def get_development_cors():
    """Get CORS configuration for development environment."""
    return {
        "allow_origins": [
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "*"  # Allow all in development
        ],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"]
    }

def get_production_cors():
    """Get CORS configuration for production environment."""
    return {
        "allow_origins": [
            "https://yourdomain.com",
            "https://www.yourdomain.com"
        ],
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "Accept",
            "Origin"
        ]
    }

def get_cors_config_for_environment(environment: str = None) -> dict:
    """
    Get CORS configuration based on environment.
    """
    if not environment:
        environment = os.getenv("ENVIRONMENT", "production").lower()
    
    if environment in ["development", "dev", "debug"]:
        return get_development_cors()
    else:
        return get_production_cors()
