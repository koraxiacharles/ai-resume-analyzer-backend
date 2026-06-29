from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import re

from app.config import settings

def _fix_render_postgres_url(url: str) -> str:
    """Fix common Render PostgreSQL URL issues"""
    if not url:
        return url
    
    # Replace postgres:// with postgresql:// (SQLAlchemy 1.4+ requirement)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    return url

# Fix the database URL if needed
DATABASE_URL = _fix_render_postgres_url(settings.DATABASE_URL)

# Create engine with production settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connections before using
    pool_size=5,             # Limit connections (free tier friendly)
    max_overflow=10,         # Allow some overflow
    pool_recycle=3600,       # Recycle connections hourly
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()