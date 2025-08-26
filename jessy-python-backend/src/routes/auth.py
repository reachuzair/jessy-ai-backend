from fastapi import APIRouter, Depends
from src.controllers.auth_controller import signup, signin, verify_email, resend_email_verification_otp, request_password_reset

router = APIRouter()

router.post("/signup")(signup)
router.post("/signin")(signin)
router.post("/verify-email")(verify_email)
router.post("/resend-email-verification-otp")(resend_email_verification_otp)
router.post("/request-password-reset")(request_password_reset)
