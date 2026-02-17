from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.core.security import get_current_user
from app.models import user, product, verification
import cloudinary
from decouple import config

# Create database tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Anti-Counterfeit Application...")
    yield
    # Shutdown
    print("Shutting down Anti-Counterfeit Application...")


app = FastAPI(
    title="Anti-Counterfeit Blockchain API",
    description="A comprehensive API for barcode-based blockchain anti-counterfeit application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cloudinary.config(
    cloud_name=config("CLOUDINARY_CLOUD_NAME"),
    api_key=config("CLOUDINARY_API_KEY"),
    api_secret=config("CLOUDINARY_API_SECRET"),
)

# Security
security = HTTPBearer()

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Anti-Counterfeit Blockchain API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}


@app.get("/protected")
async def protected_route(current_user=Depends(get_current_user)):
    return {"message": "This is a protected route", "user": current_user.email}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
