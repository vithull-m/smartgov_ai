from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.utils.dependencies import get_current_user, get_optional_current_user
from app.models.models import User, UserProfile, Scheme
from app.schemas.schemas import (
    EligibilityResult,
    EligibilityEvaluationResult,
    DirectEligibilityCheckRequest,
    DirectEligibilityCheckResponse,
)
from app.services.eligibility_engine import evaluate_scheme, evaluate_scheme_detailed

router = APIRouter(prefix="/api/eligibility", tags=["Eligibility"])


@router.get("/check/{scheme_id}", response_model=EligibilityResult)
def check_eligibility_by_id(scheme_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """User profile eligibility check for a scheme."""
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Please complete your profile first")

    detailed = evaluate_scheme_detailed(scheme, profile)
    return EligibilityResult(
        scheme_id=scheme.id,
        title=scheme.title,
        match_score=detailed.match_score,
        is_eligible=detailed.is_eligible,
        status=detailed.status,
        matched_reasons=detailed.passed_conditions,
        unmatched_reasons=detailed.failed_conditions,
        missing_fields=detailed.missing_information,
        required_documents=detailed.required_documents,
        official_link=detailed.official_link,
    )


@router.post("/check", response_model=DirectEligibilityCheckResponse)
def check_eligibility_post(payload: DirectEligibilityCheckRequest, db: Session = Depends(get_db)):
    """
    Direct eligibility check with custom profile attributes.
    Supports evaluating a single scheme or all schemes in a category.
    """
    query = db.query(Scheme).filter(Scheme.is_active == True)  # noqa: E712
    if payload.scheme_id:
        query = query.filter(Scheme.id == payload.scheme_id)
    elif payload.category:
        query = query.filter(Scheme.category.ilike(f"%{payload.category}%"))

    schemes = query.all()
    if not schemes:
        if payload.scheme_id:
            raise HTTPException(status_code=404, detail="Scheme not found")
        return DirectEligibilityCheckResponse(results=[])

    results: List[EligibilityEvaluationResult] = []
    for s in schemes:
        eval_res = evaluate_scheme_detailed(s, payload.profile)
        results.append(eval_res)

    results.sort(key=lambda r: (r.is_eligible, r.match_score), reverse=True)
    return DirectEligibilityCheckResponse(results=results)
