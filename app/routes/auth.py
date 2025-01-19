from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..services.auth import (
    create_user,
    verify_user,
    authenticate_user,
    create_token
)
from ..schemas.schemas import UserCreate, Token
from ..database import get_db

router = APIRouter()

@router.post("/signup/client", response_model=dict)
async def signup_client(user: UserCreate, db: Session = Depends(get_db)):
    user = await create_user(db, user, "client")
    return {
        "message": "Verification email sent",
        "verification_url": f"/verify-email/{user.verification_token}"
    }

@router.post("/verify-email/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    if await verify_user(db, token):
        return {"message": "Email verified successfully"}
    raise HTTPException(status_code=400, detail="Invalid verification token")

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"} 