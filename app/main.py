from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import auth, resume

# Create tables on startup if they don't exist yet.
# For evolving schemas in production, migrate to Alembic (see README).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Resume Analyzer",
    description=(
        "Register, log in, and analyze your resume against a job description "
        "using a Gemini-powered ATS agent."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resume.router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "ai-resume-analyzer"}