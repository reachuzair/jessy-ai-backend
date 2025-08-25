from fastapi import HTTPException, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.user import User
from src.config.database import get_db
from src.utils.jwt import generate_access_token, generate_refresh_token
import logging

logger = logging.getLogger("auth")

#signup function that checks for already existing user as well
async def signup(email: str, password: str, db: AsyncSession = Depends(get_db)):
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists with this email")

    new_user = User(email=email, role="user")
    new_user.hash_password(password)
    db.add(new_user)
    await db.commit()
    return {"message": "User created successfully", "user": {"id": new_user.id, "email": new_user.email, "role": new_user.role}}

#sign in function
async def signin(email: str, password: str, response: Response, db: AsyncSession = Depends(get_db)):
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or not user.verify_password(password):
        raise HTTPException(status_code=403, detail="Invalid credentials")

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=6 * 60 * 60)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=7 * 24 * 60 * 60)

    return {"message": "Sign-in successful", "user": {"id": user.id, "email": user.email, "role": user.role}}
