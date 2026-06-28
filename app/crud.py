from typing import Optional
from sqlalchemy.orm import Session
from app import models, schemas
from app.security import hash_password


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user_in: schemas.UserCreate):
    user = models.User(
        email=user_in.email,
        profession=user_in.profession,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_resume(db, user_id, filename, raw_text):
    r = models.Resume(user_id=user_id, filename=filename, raw_text=raw_text)
    db.add(r); db.commit(); db.refresh(r)
    return r

def get_resume(db, user_id, resume_id):
    return db.query(models.Resume).filter(
        models.Resume.id == resume_id,
        models.Resume.user_id == user_id
    ).first()

def create_analysis(db, user_id, resume_id, job_role, job_description, result: schemas.AnalysisResult):
    a = models.Analysis(
        user_id=user_id, resume_id=resume_id,
        job_role=job_role, job_description=job_description,
        ats_score=result.ats_score,
        score_reason=result.score_reason,
        seniority_level=result.seniority_level,
        matched_keywords=result.matched_keywords,
        missing_keywords=result.missing_keywords,
        section_health=[s.model_dump() for s in result.section_health],
        weak_bullets=result.weak_bullets,
        improved_bullets=result.improved_bullets,
        strengths=result.strengths,
        weaknesses=result.weaknesses,
        top_feedback=result.top_feedback,
    )
    db.add(a); db.commit(); db.refresh(a)
    return a

def get_user_analyses(db, user_id):
    return (db.query(models.Analysis)
            .filter(models.Analysis.user_id == user_id)
            .order_by(models.Analysis.created_at.desc())
            .all())

def get_analysis(db, user_id, analysis_id):
    return db.query(models.Analysis).filter(
        models.Analysis.id == analysis_id,
        models.Analysis.user_id == user_id
    ).first()
