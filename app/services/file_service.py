from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from ..models.models import File, User
from ..utils.security import generate_download_token
import os
import shutil
from ..config import settings

async def upload_file(db: Session, file: UploadFile, user: User) -> dict:
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{generate_download_token()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create database entry
    db_file = File(
        filename=file.filename,
        file_path=file_path,
        uploaded_by=user.id,
        download_token=generate_download_token()
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return {"file_id": db_file.id}

async def get_file_list(db: Session) -> list:
    files = db.query(File).all()
    return [{"id": file.id, "filename": file.filename} for file in files]

async def generate_download_url(db: Session, file_id: int) -> str:
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return f"/files/download/{file.download_token}"

async def validate_download_token(db: Session, token: str) -> File:
    file = db.query(File).filter(File.download_token == token).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file 