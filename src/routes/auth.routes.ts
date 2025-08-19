import express from "express";
import {
  signup,
  signin,
  requestPasswordReset,
  verifyEmail,
  resendEmailVerificationOtp
} from "../controllers/auth.controller";

const router = express.Router();

router.post("/signup", signup);
router.post("/signin", signin);
router.post("/verify-email", verifyEmail);
router.post("/resend-email-verification-otp", resendEmailVerificationOtp);
router.post("/request-password-reset", requestPasswordReset);

export default router;
