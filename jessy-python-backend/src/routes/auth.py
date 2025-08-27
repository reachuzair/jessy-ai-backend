from fastapi import APIRouter, Depends
from src.controllers.auth_controller import (
    signup, signin, verify_email, resend_email_verification_otp, 
    request_password_reset, reset_password, logout, revoke_all_user_tokens
)

router = APIRouter()

router.post("/signup")(signup)
router.post("/signin")(signin)
router.post("/verify-email")(verify_email)
router.post("/resend-email-verification-otp")(resend_email_verification_otp)
router.post("/request-password-reset")(request_password_reset)
router.post("/reset-password")(reset_password)
router.post("/logout")(logout)
router.post("/revoke-all-tokens/{user_id}")(revoke_all_user_tokens)
