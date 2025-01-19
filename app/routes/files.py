from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import os

from app.services.file_service import (
    upload_file,
    get_file_list,
    generate_download_url,
    validate_download_token
)
from app.services.auth import get_current_user
from app.database import get_db
from app.models.models import UserType

router = APIRouter()

ALLOWED_EXTENSIONS = {'.pptx', '.docx', '.xlsx'}

@router.post("/upload")
async def upload_file_route(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.user_type != UserType.OPS:
        raise HTTPException(status_code=403, detail="Only OPS users can upload files")
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    return await upload_file(db, file, current_user)

@router.get("/files")
async def list_files(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.user_type != UserType.CLIENT:
        raise HTTPException(status_code=403, detail="Only CLIENT users can list files")
    
    return await get_file_list(db)

@router.get("/download-file/{file_id}")
async def get_download_link(
    file_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.user_type != UserType.CLIENT:
        raise HTTPException(status_code=403, detail="Only CLIENT users can download files")
    
    download_url = await generate_download_url(db, file_id)
    return {
        "download_link": download_url,
        "message": "success"
    } 