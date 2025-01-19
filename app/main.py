from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, files
from .database import create_tables

app = FastAPI(title="Secure File Sharing System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(files.router, prefix="/files", tags=["Files"])

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
def read_root():
    return {"message": "Welcome to Secure File Sharing System"} 