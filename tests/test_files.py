import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://test:test@localhost/test_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_upload_file():
    # Login as OPS user first
    login_response = client.post(
        "/login",
        data={"username": "ops@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Test file upload
    with open("test_file.xlsx", "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("test_file.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == 200
    assert "file_id" in response.json() 