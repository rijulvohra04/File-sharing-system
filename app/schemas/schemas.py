from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class UserType(str, Enum):
    OPS = "ops"
    CLIENT = "client"

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    user_type: Optional[UserType] = UserType.CLIENT

class User(UserBase):
    id: int
    is_verified: bool
    user_type: UserType

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 