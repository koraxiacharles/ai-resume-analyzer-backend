from datetime import datetime
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    profession = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="owner", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="owner", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="resumes")
    analyses = relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_role = Column(String, nullable=True)
    job_description = Column(Text, nullable=False)

    ats_score = Column(Integer, nullable=False)
    score_reason = Column(Text, nullable=False)
    seniority_level = Column(String, default="unknown")
    matched_keywords = Column(JSON, nullable=False, default=list)
    missing_keywords = Column(JSON, nullable=False, default=list)
    section_health = Column(JSON, nullable=False, default=list)
    weak_bullets = Column(JSON, nullable=False, default=list)
    improved_bullets = Column(JSON, nullable=False, default=list)
    strengths = Column(JSON, nullable=False, default=list)
    weaknesses = Column(JSON, nullable=False, default=list)
    top_feedback = Column(JSON, nullable=False, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="analyses")
    resume = relationship("Resume", back_populates="analyses")
