import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import os
import uuid

JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret")

# Generate Access Token
def generate_access_token(user):
    jti = str(uuid.uuid4())  # Unique token identifier
    payload = {
        "id": str(user.id),
        "email": user.email,
        "role": user.role,
        "jti": jti,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(hours=6)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# Generate Refresh Token
def generate_refresh_token(user):
    jti = str(uuid.uuid4())  # Unique token identifier
    payload = {
        "id": str(user.id),
        "email": user.email,
        "jti": jti,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# Verify Token
def verify_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def is_token_blacklisted(token_jti: str, db: AsyncSession) -> bool:
    """Check if a token is blacklisted"""
    from src.models.token_blacklist import TokenBlacklist
    
    result = await db.execute(
        select(TokenBlacklist).where(TokenBlacklist.token_jti == token_jti)
    )
    blacklisted_token = result.scalars().first()
    return blacklisted_token is not None

async def blacklist_token(token_jti: str, token_type: str, user_id: str, expires_at: datetime, db: AsyncSession):
    """Add a token to the blacklist"""
    from src.models.token_blacklist import TokenBlacklist
    
    blacklisted_token = TokenBlacklist(
        token_jti=token_jti,
        token_type=token_type,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(blacklisted_token)
    await db.commit()

async def cleanup_expired_blacklisted_tokens(db: AsyncSession):
    """Remove expired tokens from blacklist"""
    from src.models.token_blacklist import TokenBlacklist
    
    await db.execute(
        TokenBlacklist.__table__.delete().where(
            TokenBlacklist.expires_at < datetime.utcnow()
        )
    )
    await db.commit()
