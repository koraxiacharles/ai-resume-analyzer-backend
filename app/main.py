from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from sqlalchemy import text

from app.config import settings
from app.database import Base, engine, SessionLocal
from app.routers import auth, resume

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Resume Analyzer",
    description=(
        "Register, log in, and analyze your resume against a job description "
        "using a Gemini-powered ATS agent."
    ),
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(resume.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    logger.info("🚀 Starting AI Resume Analyzer API...")
    try:
        # Create all tables if they don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables verified/created successfully")
        
        # Test database connection
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            logger.info("✅ Database connection verified")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        # Don't crash - the app might recover on next request


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Render"""
    try:
        # Test database connectivity
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {
            "status": "healthy",
            "service": "ai-resume-analyzer",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "ai-resume-analyzer",
            "error": str(e)
        }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to AI Resume Analyzer API",
        "version": "1.0.0",
        "docs": "/docs"
    }