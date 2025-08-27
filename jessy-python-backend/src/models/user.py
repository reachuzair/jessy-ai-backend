from sqlalchemy import Column, String, DateTime, Date, func, Boolean 
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
import uuid

Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    username = Column(String(255), unique=True, nullable=True)  # Made nullable since it's not always provided
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_otp = Column(String(255), nullable=True)  # Increased for bcrypt hash
    email_verification_otp_expires_at = Column(DateTime(timezone=True), nullable=True)
    password_reset_otp = Column(String(255), nullable=True)  # Increased for bcrypt hash
    password_reset_otp_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(Date, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password_hash)

    def hash_password(self, plain_password: str):
        self.password_hash = pwd_context.hash(plain_password)
