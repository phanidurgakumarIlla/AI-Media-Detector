from datetime import datetime, timedelta
from typing import Optional

import os
from dotenv import load_dotenv

# Load Environment Variables from .env file (Phase 49 Secure Bridge)
load_dotenv()

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel

import random
import string
import logging

from database import get_db
import models

# Configure logging to show OTP in terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRET_KEY = "super-secret-iron-man-ai-detector-key-12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class VerifyOTP(BaseModel):
    username: str
    otp_code: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    username: str
    role: str
    email: Optional[str] = None
    is_verified: bool = False

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email Configuration from .env
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))

def send_otp_email(receiver_email, otp_code):
    """Sends a real email if credentials exist, else falls back to console."""
    if not EMAIL_USER or not EMAIL_PASS:
        print(f"\n[WARN] [SMTP NOT CONFIGURED] Fallback OTP for {receiver_email}: {otp_code}\n")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = receiver_email
        msg['Subject'] = "AI Media Detector - Your Verification Code"

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0f0c29; color: #ffffff; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #1a1a2e; padding: 30px; border-radius: 15px; border: 1px solid #7000ff;">
                <h2 style="color: #7000ff; text-align: center;">AI Media Detector Security</h2>
                <p>Hello,</p>
                <p>Your one-time password (OTP) for account verification is:</p>
                <div style="font-size: 32px; font-weight: bold; text-align: center; color: #00d2ff; letter-spacing: 5px; margin: 20px 0;">
                    {otp_code}
                </div>
                <p>This code will expire in 10 minutes. Please do not share this code with anyone.</p>
                <hr style="border: 0; border-top: 1px solid #333;">
                <p style="font-size: 12px; color: #888; text-align: center;">🛡️ Protected by AI Media Detector Engine</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        
        print(f"[OK] Real OTP Email sent successfully to {receiver_email}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send real email: {e}")
        print(f"Fallback OTP for {receiver_email}: {otp_code}")
        return False

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    print(f"DEBUG: Registration attempt for user: {user.username}, email: {user.email}")
    try:
        # Check for existing username
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Check for existing email
        db_email = db.query(models.User).filter(models.User.email == user.email).first()
        if db_email:
            raise HTTPException(status_code=400, detail="Email already registered. Try logging in.")
        
        # Check if email is provided if not Google Auth
        if not user.email:
            raise HTTPException(status_code=400, detail="Email is required for registration")

        # First user to ever register gets the "admin" role automatically
        is_first_user = db.query(models.User).count() == 0
        role = "admin" if is_first_user else "user"
        
        otp = generate_otp()
        hashed_password = get_password_hash(user.password)
        
        # In a real app, send actual email here. For now, log to terminal.
        logger.info(f"\n\n[SECURITY] OTP for {user.email}: {otp}\n\n")
        
        new_user = models.User(
            username=user.username, 
            email=user.email,
            hashed_password=hashed_password, 
            role=role,
            otp_code=otp,
            is_verified=0
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # Simulation or Real Email: Send OTP
        send_otp_email(new_user.email, otp)
        
        return {"username": new_user.username, "email": new_user.email, "message": "OTP sent to your email. Please check your inbox (and spam)."}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"MySQL Registration Error: {str(e)} | Details: {err_msg}")

@router.post("/verify-otp")
def verify_otp(payload: VerifyOTP, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.otp_code == payload.otp_code:
        user.is_verified = 1
        user.otp_code = None # Clear after use
        db.commit()
        return {"message": "Verification successful. You can now login."}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP code")

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = db.query(models.User).filter(models.User.username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if verified
        if user.is_verified == 0:
            raise HTTPException(status_code=403, detail="Account not verified. Please verify your email via OTP.")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"MySQL Login Error: {str(e)} | Details: {traceback.format_exc()}")

# Simulated Google Auth Endpoint
@router.post("/google-auth")
def google_auth(payload: dict, db: Session = Depends(get_db)):
    # In a real app, verify the Google ID token. 
    # Here we simulate picking a Gmail from the UI.
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google email not provided")
    
    username = email.split("@")[0] # Simple username from email
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        # Create new user via Google
        is_first_user = db.query(models.User).count() == 0
        role = "admin" if is_first_user else "user"
        
        # Password not needed for Google users, but we set a dummy one
        dummy_pass = get_password_hash(generate_otp() + generate_otp())
        
        user = models.User(
            username=username, 
            email=email, 
            hashed_password=dummy_pass, 
            role=role,
            is_verified=1 # Google accounts are auto-verified
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "username": user.username}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return UserResponse(
        username=current_user.username, 
        role=current_user.role,
        email=current_user.email,
        is_verified=bool(current_user.is_verified)
    )

@router.get("/users")
def get_all_users(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Restricted to admin role only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrative privileges required to view users.")
    
    users = db.query(models.User).all()
    # Mask passwords, return only essential details
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "is_verified": bool(u.is_verified)
        } for u in users
    ]

@router.get("/admin/stats")
def get_admin_stats(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Restricted to admin role only. Returns real-time forensic counts."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrative privileges required to access analytics.")
    
    user_count = db.query(models.User).count()
    scan_count = db.query(models.AnalysisResult).count()
    
    return {
        "user_count": user_count,
        "scan_count": scan_count,
        "engine_status": "ACTIVE",
        "version": "V2.1.0"
    }
