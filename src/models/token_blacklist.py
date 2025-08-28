from sqlalchemy import Column, String, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from src.models.user import Base
import uuid

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    token_jti = Column(String(255), unique=True, nullable=False)
    token_type = Column(String(20), nullable=False)  # 'access' or 'refresh'
    user_id = Column(UUID(as_uuid=True), nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index('idx_token_blacklist_jti', 'token_jti'),
        Index('idx_token_blacklist_user_id', 'user_id'),
        Index('idx_token_blacklist_expires_at', 'expires_at'),
    )

    def __repr__(self):
        return f"<TokenBlacklist(token_jti='{self.token_jti}', user_id='{self.user_id}')>"