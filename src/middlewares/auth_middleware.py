from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from src.utils.jwt import verify_token, generate_access_token, generate_refresh_token, is_token_blacklisted, blacklist_token
from src.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.config.database import get_db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("auth")

async def handle_token_refresh(refresh_token: str, response: JSONResponse, db: AsyncSession):
    try:
        refresh_decoded = verify_token(refresh_token)
        
        # Check if refresh token is blacklisted
        if await is_token_blacklisted(refresh_decoded.get("jti", ""), db):
            logger.warning(f"Blacklisted refresh token used by user {refresh_decoded.get('id', 'unknown')}")
            raise HTTPException(status_code=401, detail="Token has been revoked")
        
        result = await db.execute(select(User).where(User.id == refresh_decoded["id"]))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found. Please login again.")

        # Verify refresh token against database
        if not user.verify_refresh_token(refresh_token):
            logger.warning(f"Invalid refresh token for user {user.id}")
            raise HTTPException(status_code=401, detail="Invalid refresh token. Please login again.")

        # Blacklist the old refresh token
        old_refresh_jti = refresh_decoded.get("jti", "")
        old_refresh_exp = datetime.fromtimestamp(refresh_decoded.get("exp", 0))
        await blacklist_token(old_refresh_jti, "refresh", str(user.id), old_refresh_exp, db)

        # Generate new tokens (token rotation)
        new_access_token = generate_access_token(user)
        new_refresh_token = generate_refresh_token(user)
        
        # Store new refresh token in database
        user.set_refresh_token(new_refresh_token)
        await db.commit()
        
        # Set new tokens in cookies
        response.set_cookie(key="access_token", value=new_access_token, httponly=True, max_age=6 * 60 * 60)
        response.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True, max_age=7 * 24 * 60 * 60)
        
        return user
    except Exception as e:
        logger.error("Refresh token validation failed", exc_info=e)
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
            
            # Check if access token is blacklisted
            if await is_token_blacklisted(decoded.get("jti", ""), db):
                logger.warning(f"Blacklisted access token used by user {decoded.get('id', 'unknown')}")
                raise HTTPException(status_code=401, detail="Token has been revoked")
            
            request.state.user = decoded
            return
    except Exception as e:
        if refresh_token:
            user = await handle_token_refresh(refresh_token, response, db)
            request.state.user = {"id": str(user.id), "email": user.email, "role": user.role}
            return

    raise HTTPException(status_code=401, detail="Unauthorized: Invalid token")
