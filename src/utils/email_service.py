import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger("email")

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.from_name = os.getenv("FROM_NAME", "Jessy AI")
        
    async def send_verification_email(self, to_email: str, otp: str) -> bool:
        """Send email verification OTP"""
        try:
            subject = "Verify Your Email - Jessy AI"
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2c3e50; text-align: center;">Email Verification</h2>
                        <p>Hello,</p>
                        <p>Thank you for registering with Jessy AI. Please use the following OTP to verify your email address:</p>
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                            <h1 style="color: #007bff; margin: 0; font-size: 36px; letter-spacing: 5px;">{otp}</h1>
                        </div>
                        <p>This OTP will expire in 10 minutes for security reasons.</p>
                        <p>If you didn't request this verification, please ignore this email.</p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                        <p style="color: #666; font-size: 12px; text-align: center;">
                            This is an automated message from Jessy AI. Please do not reply to this email.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            return await self._send_email(to_email, subject, html_body)
            
        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")
            return False
    
    async def send_password_reset_email(self, to_email: str, otp: str) -> bool:
        """Send password reset OTP"""
        try:
            subject = "Password Reset - Jessy AI"
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #dc3545; text-align: center;">Password Reset</h2>
                        <p>Hello,</p>
                        <p>You requested a password reset for your Jessy AI account. Please use the following OTP to reset your password:</p>
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                            <h1 style="color: #dc3545; margin: 0; font-size: 36px; letter-spacing: 5px;">{otp}</h1>
                        </div>
                        <p>This OTP will expire in 10 minutes for security reasons.</p>
                        <p>If you didn't request this password reset, please ignore this email and ensure your account is secure.</p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                        <p style="color: #666; font-size: 12px; text-align: center;">
                            This is an automated message from Jessy AI. Please do not reply to this email.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            return await self._send_email(to_email, subject, html_body)
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {str(e)}")
            return False
    
    async def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send email using SMTP"""
        try:
            if not self.email_user or not self.email_password:
                logger.error("Email credentials not configured")
                return False
                
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.email_user}>"
            msg['To'] = to_email
            
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
                
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False

# Singleton instance
email_service = EmailService()