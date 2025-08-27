from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.controllers.auth_controller import (
    signup,
    signin,
    verify_email,
    resend_email_verification_otp,
    request_password_reset,
)
from src.middlewares.rate_limit import auth_rate_limit, public_rate_limit
from src.config.database import get_db
from src.models.auth_models import (
    SignupRequest,
    SigninRequest,
    VerifyEmailRequest,
    ResendOtpRequest,
    PasswordResetRequest,
)

router = APIRouter()

# Apply strict rate limiting to authentication endpoints
@router.post("/signup")
@auth_rate_limit()
async def signup_endpoint(request: Request, body: SignupRequest, db: AsyncSession = Depends(get_db)):
    return await signup(body.email, body.password, body.username, body.full_name, db)


@router.post("/signin")
@auth_rate_limit()
async def signin_endpoint(
    request: Request, 
    body: SigninRequest, 
    response: Response, 
    db: AsyncSession = Depends(get_db)
):
    return await signin(body.email, body.password, response, db)


# Apply moderate rate limiting to verification endpoints
@router.post("/verify-email")
@public_rate_limit()
async def verify_email_endpoint(request: Request, body: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    return await verify_email(body.email, body.otp, db)


@router.post("/resend-email-verification-otp")
@auth_rate_limit()
async def resend_otp_endpoint(request: Request, body: ResendOtpRequest, db: AsyncSession = Depends(get_db)):
    return await resend_email_verification_otp(body.email, db)


@router.post("/request-password-reset")
@auth_rate_limit()
async def password_reset_endpoint(request: Request, body: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    return await request_password_reset(body.email, db)
