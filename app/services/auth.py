from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import models directly
from ..models.models import User, UserType
from ..schemas.schemas import UserCreate, TokenData
from ..utils.security import (
    get_password_hash,
    verify_password,
    generate_verification_token
)
from ..config import settings
from ..database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

async def create_user(db: Session, user_data: UserCreate, user_type: str) -> User:
    # Check if user already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    verification_token = generate_verification_token()
    db_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        user_type=UserType(user_type),
        verification_token=verification_token,
        is_verified=False
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Send verification email
        await send_verification_email(user_data.email, verification_token)
        
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating user: {str(e)}"
        )

async def verify_user(db: Session, token: str) -> bool:
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Invalid verification token"
        )
    if user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Email already verified"
        )
    
    try:
        user.is_verified = True
        user.verification_token = None
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error verifying user: {str(e)}"
        )

async def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your email first"
        )
    return user

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

async def send_verification_email(email: str, token: str):
    verification_url = f"http://localhost:8000/auth/verify-email/{token}"
    
    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify your email"
    message["From"] = settings.SMTP_USER
    message["To"] = email

    # Create HTML version of message
    html = f"""
    <html>
        <body>
            <h1>Welcome to Secure File Sharing System</h1>
            <p>Please verify your email by clicking on the link below:</p>
            <p><a href="{verification_url}">Verify Email</a></p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
    </html>
    """
    
    message.attach(MIMEText(html, "html"))
    
    try:
        # Create SMTP connection
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        
        # Send email
        server.sendmail(
            settings.SMTP_USER,
            email,
            message.as_string()
        )
        server.quit()
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending verification email: {str(e)}"
        ) 