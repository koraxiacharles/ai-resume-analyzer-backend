import json
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import get_db
from app.dependencies import get_current_user
from app.services.ai_service import analyze_resume, regenerate_resume
from app.services.pdf_parser import extract_text_from_pdf

router = APIRouter(prefix="/resume", tags=["Resume Analysis"])
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/analyze", response_model=schemas.AnalysisResponse)
async def analyze(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    job_role: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a PDF resume.")
    if not job_description.strip():
        raise HTTPException(400, "Job description is required.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(400, "File is empty.")
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(400, "PDF must be under 5 MB.")

    try:
        resume_text = extract_text_from_pdf(file_bytes)
        result = analyze_resume(resume_text, job_description)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(500, str(e))
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {e}")

    resume = crud.create_resume(db, current_user.id, file.filename, resume_text)
    crud.create_analysis(db, current_user.id, resume.id, job_role, job_description, result)

    return schemas.AnalysisResponse(data=result, resume_preview=resume_text[:500])


@router.post("/regenerate", response_model=schemas.RegenResponse)
async def regenerate(
    req: schemas.RegenRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    analysis = crud.get_analysis(db, current_user.id, req.analysis_id)
    if not analysis:
        raise HTTPException(404, "Analysis not found.")

    resume = crud.get_resume(db, current_user.id, analysis.resume_id)
    if not resume:
        raise HTTPException(404, "Resume not found.")

    analysis_dict = {
        "ats_score": analysis.ats_score,
        "missing_keywords": analysis.missing_keywords,
        "section_health": analysis.section_health,
        "weak_bullets": analysis.weak_bullets,
        "improved_bullets": analysis.improved_bullets,
        "strengths": analysis.strengths,
        "weaknesses": analysis.weaknesses,
        "top_feedback": analysis.top_feedback,
    }

    try:
        html = regenerate_resume(
            resume_text=resume.raw_text,
            analysis_json=analysis_dict,
            job_role=req.job_role or analysis.job_role or "",
            job_description=req.job_description or analysis.job_description or "",
        )
    except Exception as e:
        raise HTTPException(500, f"Regeneration failed: {e}")

    return schemas.RegenResponse(html=html)


@router.get("/history", response_model=list[schemas.AnalysisOut])
def history(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_user_analyses(db, current_user.id)


@router.get("/history/{analysis_id}", response_model=schemas.AnalysisOut)
def history_detail(analysis_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    a = crud.get_analysis(db, current_user.id, analysis_id)
    if not a:
        raise HTTPException(404, "Analysis not found.")
    return a
