from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class UserType(enum.Enum):
    OPS = "ops"
    CLIENT = "client"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    user_type = Column(Enum(UserType))
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)

class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    file_path = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    download_token = Column(String, unique=True, index=True) 