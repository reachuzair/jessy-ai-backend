import random
import string
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

class OTPService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP of specified length"""
        return ''.join(random.choices(string.digits, k=length))
    
    def hash_otp(self, plain_otp: str) -> str:
        """Hash an OTP for secure storage"""
        return self.pwd_context.hash(plain_otp)
    
    def verify_otp(self, plain_otp: str, hashed_otp: str) -> bool:
        """Verify a plain OTP against its hash"""
        return self.pwd_context.verify(plain_otp, hashed_otp)
    
    def get_otp_expiry(self, minutes: int = 10) -> datetime:
        """Get OTP expiry time (default 10 minutes from now)"""
        return datetime.now(timezone.utc) + timedelta(minutes=minutes)
    
    def is_otp_expired(self, expiry_time: datetime) -> bool:
        """Check if OTP has expired"""
        current_time = datetime.now(timezone.utc)
        # Handle both timezone-aware and timezone-naive datetimes
        if expiry_time.tzinfo is None:
            expiry_time = expiry_time.replace(tzinfo=timezone.utc)
        return current_time > expiry_time
    
    def is_otp_valid(self, provided_otp: str, stored_otp_hash: str, expiry_time: datetime) -> bool:
        """Validate OTP by checking hash and expiry"""
        if not provided_otp or not stored_otp_hash or not expiry_time:
            return False
        
        if self.is_otp_expired(expiry_time):
            return False
            
        return self.verify_otp(provided_otp, stored_otp_hash)

otp_service = OTPService()