from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True) # Gmail for OTP
    hashed_password = Column(String(255))
    role = Column(String(50), default="user") # "user" or "admin"
    is_verified = Column(Integer, default=0) # 0 = unverified, 1 = verified
    otp_code = Column(String(10), nullable=True) # 6-digit verification code

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    username = Column(String(255)) # Added for direct readability in SQL
    filename = Column(String(255))
    verdict = Column(String(50)) # "AI Generated" or "Authentic"
    ai_score = Column(Float)
    algorithm = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
