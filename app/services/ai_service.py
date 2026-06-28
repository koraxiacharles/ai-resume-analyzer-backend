"""
AI ATS Agent — powered by Google Gemini.
Handles section health, strengths/weaknesses, seniority, and resume regeneration.
"""

import json
import re
import google.generativeai as genai

from app.config import settings
from app.schemas import AnalysisResult, SectionHealth

_model = None
_regen_model = None


def _get_model():
    global _model
    if _model is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set.")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                response_mime_type="application/json",
            ),
        )
    return _model


def _get_regen_model():
    global _regen_model
    if _regen_model is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set.")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _regen_model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=4000,
            ),
        )
    return _regen_model


ANALYSIS_PROMPT_TEMPLATE = """You are an expert ATS analyst and professional resume coach.
Analyze the resume (and job description if provided) and return ONLY a valid JSON object:

{{
  "ats_score": <integer 0-100>,
  "score_reason": "<one sentence>",
  "seniority_level": "<junior|mid|senior|lead|unknown>",
  "matched_keywords": ["keyword", ...],
  "missing_keywords": ["keyword", ...],
  "section_health": [
    {{
      "name": "<section name>",
      "score": <0-100>,
      "status": "<strong|needs_work|missing>",
      "comment": "<one short sentence>"
    }}
  ],
  "weak_bullets": ["original bullet", ...],
  "improved_bullets": ["rewritten bullet", ...],
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
  "top_feedback": ["tip 1", "tip 2", "tip 3"]
}}

Rules:
- section_health: evaluate EVERY section found in the resume (Summary, Work Experience,
  Skills, Education, Projects, Certifications, etc.). If a common section is MISSING
  entirely, include it with status "missing" and score 0.
- strong = score 75-100, needs_work = 30-74, missing = 0-29
- matched_keywords: up to 15, from job description appearing in resume
- missing_keywords: up to 15, important JD terms absent from resume
- weak_bullets: 2-4 bullets that lack metrics or action verbs
- improved_bullets: same count, rewritten with metrics + strong verbs + JD keywords
- strengths: exactly 3 concrete strengths
- weaknesses: exactly 3 concrete areas to improve
- top_feedback: exactly 3 actionable tips
- Return ONLY the JSON object, no markdown, no commentary.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}"""


REGEN_PROMPT_TEMPLATE = """You are a professional resume writer.
Given the original resume text, its ATS analysis, and a target job description,
produce a complete, improved HTML resume.

Requirements:
- Return ONLY a complete HTML document (<!DOCTYPE html> ... </html>)
- Clean, single-column, print-optimized layout with white background
- Use system fonts (font-family: Georgia, serif for name; Arial, sans-serif for body)
- Embed all CSS inside a <style> tag — no external dependencies
- Incorporate missing keywords naturally, fix all weak bullets with metrics
- Fix every section flagged as "needs_work" or "missing" in the analysis
- Target the provided job role
- Include: header (name, contact), summary, skills, experience, education, projects if present
- Appropriate for printing at A4 / Letter via browser print dialog
- @media print: hide scrollbars, ensure page-break-avoid on sections

TARGET ROLE: {job_role}

ORIGINAL RESUME:
{resume_text}

ATS ANALYSIS:
{analysis_json}

JOB DESCRIPTION:
{job_description}"""


def analyze_resume(resume_text: str, job_description: str) -> AnalysisResult:
    if not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    model = _get_model()

    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        resume_text=resume_text[:12000],
        job_description=job_description[:8000],
    )

    response = model.generate_content(prompt)

    raw = response.text
    if not raw:
        raise ValueError("Empty response from Gemini.")

    # Strip markdown fences if present (safety net)
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {e}\nRaw: {raw[:300]}")

    # Validate section_health sub-objects
    sections = []
    for s in data.get("section_health", []):
        sections.append(SectionHealth(
            name=s.get("name", "Unknown"),
            score=max(0, min(100, int(s.get("score", 0)))),
            status=s.get("status", "needs_work"),
            comment=s.get("comment", ""),
        ))
    data["section_health"] = sections

    try:
        return AnalysisResult(**data)
    except Exception as e:
        raise ValueError(f"Schema mismatch: {e}")


def regenerate_resume(
    resume_text: str,
    analysis_json: dict,
    job_role: str,
    job_description: str,
) -> str:
    model = _get_regen_model()

    prompt = REGEN_PROMPT_TEMPLATE.format(
        job_role=job_role or "Not specified",
        resume_text=resume_text[:10000],
        analysis_json=json.dumps(analysis_json, indent=2)[:4000],
        job_description=job_description[:4000],
    )

    response = model.generate_content(prompt)
    html = response.text or ""

    # Ensure we return only the HTML
    if "<!DOCTYPE" in html:
        html = html[html.index("<!DOCTYPE"):]
    elif "<html" in html:
        html = html[html.index("<html"):]

    return html