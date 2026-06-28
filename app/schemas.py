from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    profession: str = Field(..., min_length=2, description="e.g. Software Engineer")
    password: str = Field(..., min_length=8)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    profession: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ── Resume Section Health ────────────────────────────────────────────────────

class SectionHealth(BaseModel):
    """How well a specific resume section is written."""
    name: str              # e.g. "Work Experience", "Summary", "Skills"
    score: int = Field(..., ge=0, le=100)
    status: str            # "strong" | "needs_work" | "missing"
    comment: str           # one-line explanation


# ── AI Analysis Result ────────────────────────────────────────────────────────

class AnalysisResult(BaseModel):
    ats_score: int = Field(..., ge=0, le=100)
    score_reason: str
    seniority_level: str = "unknown"   # junior | mid | senior | lead | unknown

    # Keywords
    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)

    # Section-level health (the key new data)
    section_health: List[SectionHealth] = Field(default_factory=list)

    # Bullets
    weak_bullets: List[str] = Field(default_factory=list)
    improved_bullets: List[str] = Field(default_factory=list)

    # Narrative
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    top_feedback: List[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    success: bool = True
    data: AnalysisResult
    resume_preview: str


class AnalysisOut(AnalysisResult):
    id: int
    resume_id: int
    job_role: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Resume Regeneration ───────────────────────────────────────────────────────

class RegenRequest(BaseModel):
    analysis_id: int
    job_role: Optional[str] = None
    job_description: Optional[str] = None


class RegenResponse(BaseModel):
    success: bool = True
    html: str          # complete HTML resume ready to print-to-PDF
