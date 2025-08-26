from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from src.utils.jwt import verify_token, generate_access_token
from src.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.config.database import get_db
import logging

logger = logging.getLogger("auth")

async def handle_token_refresh(refresh_token: str, response: JSONResponse, db: AsyncSession):
    try:
        refresh_decoded = verify_token(refresh_token)
        result = await db.execute(select(User).where(User.id == refresh_decoded["id"]))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found. Please login again.")

        new_access_token = generate_access_token(user)
        response.set_cookie(key="access_token", value=new_access_token, httponly=True, max_age=6 * 60 * 60)
        return user
    except Exception as e:
        logger.error("Refresh token is also expired", exc_info=e)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        raise HTTPException(status_code=401, detail="Session expired. Please login again.")

async def auth(request: Request, response: JSONResponse, db: AsyncSession = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    if not access_token and not refresh_token:
        raise HTTPException(status_code=401, detail="Unauthorized: No tokens provided")

    try:
        if access_token:
            decoded = verify_token(access_token)
            request.state.user = decoded
            return
    except Exception as e:
        if refresh_token:
            user = await handle_token_refresh(refresh_token, response, db)
            request.state.user = user
            return

    raise HTTPException(status_code=401, detail="Unauthorized: Invalid token")
