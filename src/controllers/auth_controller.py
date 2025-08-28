from fastapi import HTTPException, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.user import User
from src.config.database import get_db
from src.utils.jwt import generate_access_token, generate_refresh_token
from src.utils.email_service import email_service
from src.utils.otp_service import otp_service
from datetime import datetime
import logging

logger = logging.getLogger("auth")

#signup function that checks for already existing user as well
async def signup(email: str, password: str, username: str, full_name: str, db: AsyncSession):
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists with this email")

    # Generate email verification OTP
    verification_otp = otp_service.generate_otp()
    otp_hash = otp_service.hash_otp(verification_otp)
    otp_expiry = otp_service.get_otp_expiry()

    new_user = User(
        email=email,
        username=username,
        full_name=full_name,
        role="user",
        is_email_verified=False,
        email_verification_otp=otp_hash,  # Store hashed OTP
        email_verification_otp_expires_at=otp_expiry
    )
    new_user.hash_password(password)
    db.add(new_user)
    await db.commit()

    # Send verification email
    email_sent = await email_service.send_verification_email(email, verification_otp)
    
    if not email_sent:
        logger.warning(f"Failed to send verification email to {email}")
        return {
            "message": "User created successfully, but failed to send verification email. Please request a new verification code.",
            "user": {"id": new_user.id, "email": new_user.email, "role": new_user.role, "is_email_verified": False}
        }

    return {
        "message": "User created successfully. Please check your email for verification code.",
        "user": {"id": new_user.id, "email": new_user.email, "role": new_user.role, "is_email_verified": False}
    }

#sign in function
async def signin(email: str, password: str, response: Response, db: AsyncSession):
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or not user.verify_password(password):
        raise HTTPException(status_code=403, detail="Invalid credentials")

    # Check if email is verified
    if not user.is_email_verified:
        raise HTTPException(
            status_code=403, 
            detail="Please verify your email before signing in. Check your email for verification code."
        )

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    # Store refresh token in database
    user.set_refresh_token(refresh_token)
    user.last_login = datetime.now().date()
    await db.commit()

    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=6 * 60 * 60)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=7 * 24 * 60 * 60)

    return {"message": "Sign-in successful", "user": {"id": user.id, "email": user.email, "role": user.role}}

# Email verification function
async def verify_email(email: str, otp: str, db: AsyncSession):
    if not email or not otp:
        raise HTTPException(status_code=400, detail="Email and OTP are required")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_email_verified:
        raise HTTPException(status_code=400, detail="Email is already verified")

    # Validate OTP
    if not otp_service.is_otp_valid(
        otp, 
        user.email_verification_otp, 
        user.email_verification_otp_expires_at
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Mark email as verified and clear OTP
    user.is_email_verified = True
    user.email_verification_otp = None
    user.email_verification_otp_expires_at = None
    await db.commit()

    return {
        "message": "Email verified successfully", 
        "user": {"id": user.id, "email": user.email, "is_email_verified": True}
    }

# Resend email verification OTP function
async def resend_email_verification_otp(email: str, db: AsyncSession):
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_email_verified:
        raise HTTPException(status_code=400, detail="Email is already verified")

    # Generate new OTP
    verification_otp = otp_service.generate_otp()
    otp_hash = otp_service.hash_otp(verification_otp)
    otp_expiry = otp_service.get_otp_expiry()

    user.email_verification_otp = otp_hash  # Store hashed OTP
    user.email_verification_otp_expires_at = otp_expiry
    await db.commit()

    # Send verification email
    email_sent = await email_service.send_verification_email(email, verification_otp)
    
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send verification email")

    return {"message": "Verification code sent successfully"}

# Request password reset function
async def request_password_reset(email: str, db: AsyncSession):
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if not user:
        # Don't reveal if user exists for security
        return {"message": "If an account with this email exists, a password reset code has been sent"}
    
    if not user.is_email_verified:
        raise HTTPException(status_code=400, detail="Please verify your email first")

    # Generate password reset OTP
    reset_otp = otp_service.generate_otp()
    otp_hash = otp_service.hash_otp(reset_otp)
    otp_expiry = otp_service.get_otp_expiry()

    user.password_reset_otp = otp_hash  # Store hashed OTP
    user.password_reset_otp_expires_at = otp_expiry
    await db.commit()

    # Send password reset email
    email_sent = await email_service.send_password_reset_email(email, reset_otp)  # Send plain OTP
    
    if not email_sent:
        logger.error(f"Failed to send password reset email to {email}")

    return {"message": "If an account with this email exists, a password reset code has been sent"}

# Reset password function
async def reset_password(email: str, otp: str, new_password: str, db: AsyncSession):
    if not email or not otp or not new_password:
        raise HTTPException(status_code=400, detail="Email, OTP, and new password are required")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate OTP
    if not otp_service.is_otp_valid(
        otp, 
        user.password_reset_otp, 
        user.password_reset_otp_expires_at
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Update password and clear reset OTP
    user.hash_password(new_password)
    user.password_reset_otp = None
    user.password_reset_otp_expires_at = None
    await db.commit()

    return {"message": "Password reset successfully"}

# Logout function with token blacklisting
async def logout(request: Request, response: Response, db: AsyncSession):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    # Clear cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    
    # Blacklist tokens if they exist
    if access_token:
        try:
            from src.utils.jwt import verify_token, blacklist_token
            decoded_access = verify_token(access_token)
            access_jti = decoded_access.get("jti", "")
            access_exp = datetime.fromtimestamp(decoded_access.get("exp", 0))
            user_id = decoded_access.get("id", "")
            await blacklist_token(access_jti, "access", user_id, access_exp, db)
        except Exception as e:
            logger.warning(f"Failed to blacklist access token: {e}")
    
    if refresh_token:
        try:
            from src.utils.jwt import verify_token, blacklist_token
            decoded_refresh = verify_token(refresh_token)
            refresh_jti = decoded_refresh.get("jti", "")
            refresh_exp = datetime.fromtimestamp(decoded_refresh.get("exp", 0))
            user_id = decoded_refresh.get("id", "")
            await blacklist_token(refresh_jti, "refresh", user_id, refresh_exp, db)
            
            # Invalidate refresh token in user record
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            if user:
                user.invalidate_refresh_token()
                await db.commit()
        except Exception as e:
            logger.warning(f"Failed to blacklist refresh token: {e}")
    
    return {"message": "Logged out successfully"}

# Function to revoke all user tokens (useful for security incidents)
async def revoke_all_user_tokens(user_id: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Invalidate refresh token in database
    user.invalidate_refresh_token()
    await db.commit()
    
    return {"message": "All user tokens have been revoked"}