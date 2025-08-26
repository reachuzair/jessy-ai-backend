import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
import os

JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret")

# Generate Access Token
def generate_access_token(user):
    payload = {
        "id": str(user.id),
        "email": user.email,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=6)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# Generate Refresh Token
def generate_refresh_token(user):
    payload = {
        "id": str(user.id),
        "email": user.email,
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
