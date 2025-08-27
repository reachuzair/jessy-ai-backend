"""
Configuration settings for the Jessy AI Backend.
Loads settings from environment variables with secure defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/dbname")
    
    # JWT settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your_jwt_secret_change_this_in_production")
    JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_HOURS", "6"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Environment settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production").lower()
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    # Redis settings (for rate limiting)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Rate limiting settings
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    
    # CORS settings
    CORS_ALLOWED_ORIGINS: str = os.getenv("CORS_ALLOWED_ORIGINS", "")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    
    # Security settings
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT in ["development", "dev", "debug"]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"

# Create global settings instance
settings = Settings()

# Validation warnings
if settings.JWT_SECRET == "your_jwt_secret_change_this_in_production":
    print("⚠️  WARNING: Using default JWT secret! Change JWT_SECRET in production!")

if settings.is_production and settings.DEBUG_MODE:
    print("⚠️  WARNING: Debug mode is enabled in production!")

if settings.is_production and not settings.RATE_LIMIT_ENABLED:
    print("⚠️  WARNING: Rate limiting is disabled in production!")
